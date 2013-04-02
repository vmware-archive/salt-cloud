'''
Linode Cloud Module
===================

The Linode cloud module is used to control access to the Linode VPS system

Use of this module only requires the LINODE.apikey paramater to be set in
the cloud configuration file

.. code-block:: yaml

    # Linode account api key
    LINODE.apikey: JVkbSJDGHSDKUKSDJfhsdklfjgsjdkflhjlsdfffhgdgjkenrtuinv

'''

# Import python libs
import sys
import logging

# Import libcloud
from libcloud.compute.types import NodeState
from libcloud.compute.base import NodeAuthPassword

# Import salt libs
from saltcloud.libcloudfuncs import *

# Import saltcloud libs
from saltcloud.utils import namespaced_function


# Get logging started
log = logging.getLogger(__name__)


# Redirect linode functions to this module namespace
avail_locations = namespaced_function(avail_locations, globals())
avail_images = namespaced_function(avail_images, globals())
avail_sizes = namespaced_function(avail_sizes, globals())
script = namespaced_function(script, globals())
destroy = namespaced_function(destroy, globals())
list_nodes = namespaced_function(list_nodes, globals())
list_nodes_full = namespaced_function(list_nodes_full, globals())
list_nodes_select = namespaced_function(list_nodes_select, globals())


# Only load in this module if the LINODE configurations are in place
def __virtual__():
    '''
    Set up the libcloud funcstions and check for RACKSPACE configs
    '''
    if 'LINODE.apikey' in __opts__:
        log.debug('Loading Linode cloud module')
        return 'linode'
    return False


def get_conn():
    '''
    Return a conn object for the passed VM data
    '''
    driver = get_driver(Provider.LINODE)
    return driver(
            __opts__['LINODE.apikey'],
            )


def get_location(conn, vm_):
    '''
    Return the node location to use
    '''
    locations = conn.list_locations()
    # Default to Dallas if not otherwise set
    loc = 2
    if 'location' in vm_:
        loc = vm_['location']
    elif 'LINODE.location' in __opts__:
        loc = __opts__['LINODE.location']
    for location in locations:
        if str(location.id) == str(loc):
            return location
        if location.name == loc:
            return location


def get_password(vm_):
    '''
    Return the password to use
    '''
    if 'password' in vm_:
        return vm_['password']
    elif 'passwd' in vm_:
        return vm_['passwd']
    elif 'LINODE.password' in __opts__:
        return __opts__['LINODE.password']


def create(vm_):
    '''
    Create a single VM from a data dict
    '''
    log.info('Creating Cloud VM {0}'.format(vm_['name']))
    conn = get_conn()
    kwargs = {}
    kwargs['name'] = vm_['name']
    kwargs['image'] = get_image(conn, vm_)
    kwargs['size'] = get_size(conn, vm_)
    kwargs['location'] = get_location(conn, vm_)
    kwargs['auth'] = NodeAuthPassword(get_password(vm_))
    try:
        data = conn.create_node(**kwargs)
    except Exception as exc:
        err = ('Error creating {0} on LINODE\n\n'
               'The following exception was thrown by libcloud when trying to '
               'run the initial deployment: \n{1}').format(
                       vm_['name'], exc.message
                       )
        sys.stderr.write(err)
        log.error(err)
        return False

    deploy = vm_.get(
        'deploy',
        __opts__.get(
            'LINODE.deploy',
            __opts__['deploy']
        )
    )
    ret = {}
    if deploy is True:
        deploy_script = script(vm_)
        deploy_kwargs = {
            'host': data.public_ips[0],
            'username': 'root',
            'password': __opts__['LINODE.password'],
            'script': deploy_script.script,
            'name': vm_['name'],
            'deploy_command': '/tmp/deploy.sh',
            'start_action': __opts__['start_action'],
            'sock_dir': __opts__['sock_dir'],
            'conf_file': __opts__['conf_file'],
            'minion_pem': vm_['priv_key'],
            'minion_pub': vm_['pub_key'],
            'keep_tmp': __opts__['keep_tmp'],
            }

        if 'script_args' in vm_:
            deploy_kwargs['script_args'] = vm_['script_args']

        deploy_kwargs['minion_conf'] = saltcloud.utils.minion_conf_string(
            __opts__,
            vm_
        )

        # Deploy salt-master files, if necessary
        if 'make_master' in vm_ and vm_['make_master'] is True:
            deploy_kwargs['make_master'] = True
            deploy_kwargs['master_pub'] = vm_['master_pub']
            deploy_kwargs['master_pem'] = vm_['master_pem']
            master_conf = saltcloud.utils.master_conf_string(__opts__, vm_)
            if master_conf:
                deploy_kwargs['master_conf'] = master_conf

            if 'syndic_master' in master_conf:
                deploy_kwargs['make_syndic'] = True

        deployed = saltcloud.utils.deploy_script(**deploy_kwargs)
        if deployed:
            log.info('Salt installed on {0}'.format(vm_['name']))
            ret['deploy_kwargs'] = deploy_kwargs
        else:
            log.error(
                'Failed to start Salt on Cloud VM {0}'.format(
                    vm_['name']
                )
            )

    log.info(
        'Created Cloud VM {0} with the following values:'.format(
            vm_['name']
        )
    )
    for key, val in data.__dict__.items():
        ret[key] = val
        log.info('  {0}: {1}'.format(key, val))

    return ret
