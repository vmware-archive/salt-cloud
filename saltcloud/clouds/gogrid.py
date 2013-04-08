'''
GoGrid Cloud Module
====================

The GoGrid cloud module. This module interfaces with the gogrid public cloud
service. To use Salt Cloud with GoGrid log into the GoGrid web interface and
create an api key. Do this by clicking on "My Account" and then going to the
API Keys tab.

Using the old providers configuration syntax format, the ``GOGRID.apikey`` and
the ``GOGRID.sharedsecret`` configuration parameters need to be set in the
configuration file to enable interfacing with GoGrid:

.. code-block:: yaml

    # The generated api key to use
    GOGRID.apikey: asdff7896asdh789
    # The apikey's shared secret
    GOGRID.sharedsecret: saltybacon


Using the new format, set up the cloud configuration at
``/etc/salt/cloud.providers`` or ``/etc/salt/cloud.providers.d/gogrid.conf``:

.. code-block:: yaml

    my-gogrid-config:
      # The generated api key to use
      apikey: asdff7896asdh789
      # The apikey's shared secret
      sharedsecret: saltybacon

      provider: gogrid

'''

# The import section is mostly libcloud boilerplate

# Import python libs
import logging

# Import generic libcloud functions
from saltcloud.libcloudfuncs import *

# Import salt cloud libs
import saltcloud.config as config
from saltcloud.utils import namespaced_function

# Get logging started
log = logging.getLogger(__name__)

# Some of the libcloud functions need to be in the same namespace as the
# functions defined in the module, so we create new function objects inside
# this module namespace
get_size = namespaced_function(get_size, globals())
get_image = namespaced_function(get_image, globals())
avail_images = namespaced_function(avail_images, globals())
avail_sizes = namespaced_function(avail_sizes, globals())
script = namespaced_function(script, globals())
destroy = namespaced_function(destroy, globals())
list_nodes = namespaced_function(list_nodes, globals())
list_nodes_full = namespaced_function(list_nodes_full, globals())
list_nodes_select = namespaced_function(list_nodes_select, globals())


# Only load in this module is the GOGRID configurations are in place
def __virtual__():
    '''
    Set up the libcloud functions and check for GOGRID configs
    '''
    if get_configured_provider() is False:
        log.debug(
            'There is no GoGrid cloud provider configuration available. Not '
            'loading module.'
        )
        return False

    log.debug('Loading GoGrid cloud module')
    return 'gogrid'


def get_configured_provider():
    '''
    Return the first configured instance.
    '''
    return config.is_provider_configured(
        __opts__, 'gogrid', ('apikey', 'sharedsecret')
    )


def get_conn():
    '''
    Return a conn object for the passed VM data
    '''
    driver = get_driver(Provider.GOGRID)
    vm_ = get_configured_provider()
    return driver(
        config.get_config_value(
            'apikey', vm_, __opts__, search_global=False
        ),
        config.get_config_value(
            'sharedsecret', vm_, __opts__, search_global=False
        )
    )


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
    try:
        data = conn.create_node(**kwargs)
    except Exception:
        log.error(
            'Error creating {0} on GOGRID\n\n'
            'The following exception was thrown by libcloud when trying to '
            'run the initial deployment:\n'.format(
                vm_['name']
            ),
            # Show the traceback if the debug logging level is enabled
            exc_info=log.isEnabledFor(logging.DEBUG)
        )
        return False

    ret = {}
    if config.get_config_value('deploy', vm_, __opts__) is True:
        deploy_script = script(vm_)
        deploy_kwargs = {
            'host': data.public_ips[0],
            'username': 'root',
            'password': data.extra['password'],
            'script': deploy_script.script,
            'name': vm_['name'],
            'start_action': __opts__['start_action'],
            'sock_dir': __opts__['sock_dir'],
            'conf_file': __opts__['conf_file'],
            'minion_pem': vm_['priv_key'],
            'minion_pub': vm_['pub_key'],
            'keep_tmp': __opts__['keep_tmp'],
            'script_args': config.get_config_value(
                'script_args', vm_, __opts__
            )
        }

        deploy_kwargs['minion_conf'] = saltcloud.utils.minion_conf_string(
            __opts__,
            vm_
        )

        # Deploy salt-master files, if necessary
        if config.get_config_value('make_master', vm_, __opts__) is True:
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
            if __opts__.get('show_deploy_args', False) is True:
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
