'''
The AWS Cloud Module
====================

The AWS cloud module is used to interact with the Amazon Web Services system.

To use the AWS cloud module the following configuration parameters need to be
set in the main cloud config:

.. code-block:: yaml

    # The AWS API authentication id
    AWS.id: GKTADJGHEIQSXMKKRBJ08H
    # The AWS API authentication key
    AWS.key: askdjghsdfjkghWupUjasdflkdfklgjsdfjajkghs
    # The ssh keyname to use
    AWS.keyname: default
    # The amazon security group
    AWS.securitygroup: ssh_open
    # The location of the private key which corresponds to the keyname
    AWS.private_key: /root/default.pem

'''

# Import python libs
import os
import sys
import stat
import time
import logging

# Import saltcloud libs
import saltcloud.utils
from saltcloud.utils import namespaced_function
from saltcloud.libcloudfuncs import *

# Import salt libs
from salt.exceptions import SaltException

# Get logging started
log = logging.getLogger(__name__)


# Only load in this module if the AWS configurations are in place
def __virtual__():
    '''
    Set up the libcloud funcstions and check for AWS configs
    '''
    try:
        import botocore
        # Since we have botocore, we won't load the libcloud AWS module
        return False
    except ImportError:
        pass

    confs = [
        'AWS.id',
        'AWS.key',
        'AWS.keyname',
        'AWS.securitygroup',
        'AWS.private_key',
    ]
    for conf in confs:
        if conf not in __opts__:
            log.warning(
                '{0!r} not found in options. Not loading module.'.format(conf)
            )
            return False

    if not os.path.exists(__opts__['AWS.private_key']):
        raise SaltException(
            'The AWS key file {0} does not exist\n'.format(
                __opts__['AWS.private_key']
            )
        )
    keymode = str(
        oct(stat.S_IMODE(os.stat(__opts__['AWS.private_key']).st_mode))
    )
    if keymode not in ('0400', '0600'):
        raise SaltException(
            'The AWS key file {0} needs to be set to mode 0400 or '
            '0600\n'.format(
                __opts__['AWS.private_key']
            )
        )

    global avail_images, avail_sizes, script, destroy, list_nodes
    global list_nodes_full, list_nodes_select

    # open a connection in a specific region
    conn = get_conn(**{'location': get_location()})

    # Init the libcloud functions
    avail_images = namespaced_function(avail_images, globals(), (conn,))
    avail_sizes = namespaced_function(avail_sizes, globals(), (conn,))
    script = namespaced_function(script, globals(), (conn,))
    list_nodes = namespaced_function(list_nodes, globals(), (conn,))
    list_nodes_full = namespaced_function(list_nodes_full, globals(), (conn,))
    list_nodes_select = namespaced_function(list_nodes_select, globals(), (conn,))

    log.debug('Loading Libcloud AWS cloud module')
    return 'aws'


EC2_LOCATIONS = {
    'ap-northeast-1': Provider.EC2_AP_NORTHEAST,
    'ap-southeast-1': Provider.EC2_AP_SOUTHEAST,
    'eu-west-1': Provider.EC2_EU_WEST,
    'sa-east-1': Provider.EC2_SA_EAST,
    'us-east-1': Provider.EC2_US_EAST,
    'us-west-1': Provider.EC2_US_WEST,
    'us-west-2': Provider.EC2_US_WEST_OREGON
}
DEFAULT_LOCATION = 'us-east-1'

if hasattr(Provider, 'EC2_AP_SOUTHEAST2'):
    EC2_LOCATIONS['ap-southeast-2'] = Provider.EC2_AP_SOUTHEAST2


def get_conn(**kwargs):
    '''
    Return a conn object for the passed VM data
    '''
    if 'location' in kwargs:
        location = kwargs['location']
        if location not in EC2_LOCATIONS:
            raise SaltException(
                'The specified location does not seem to be valid: '
                '{0}\n'.format(
                    location
                )
            )
    else:
        location = DEFAULT_LOCATION

    driver = get_driver(EC2_LOCATIONS[location])
    return driver(
        __opts__['AWS.id'],
        __opts__['AWS.key'],
    )


def keyname(vm_):
    '''
    Return the keyname
    '''
    return str(vm_.get('keyname', __opts__.get('AWS.keyname', '')))


def securitygroup(vm_):
    '''
    Return the security group
    '''
    return vm_.get(
        'securitygroup', __opts__.get('AWS.securitygroup', 'default')
    )

    # XXX: This code won't get executed. On purpose?
    securitygroups = vm_.get(
        'securitygroup', __opts__.get('AWS.securitygroup', 'default')
    )
    if not isinstance(securitygroups, list):
        securitygroup = securitygroups
        securitygroups = [securitygroup]
    return securitygroups


def ssh_username(vm_):
    '''
    Return the ssh_username. Defaults to 'ec2-user'.
    '''
    usernames = vm_.get(
        'ssh_username', __opts__.get('AWS.ssh_username', 'ec2-user')
    )
    if not isinstance(usernames, list):
        username = usernames
        usernames = [username]
    if not 'ec2-user' in usernames:
        usernames.append('ec2-user')
    if not 'ubuntu' in usernames:
        usernames.append('ubuntu')
    if not 'admin' in usernames:
        usernames.append('admin')
    if not 'bitnami' in usernames:
        usernames.append('bitnami')
    if not 'root' in usernames:
        usernames.append('root')
    return usernames


def ssh_interface(vm_):
    '''
    Return the ssh_interface type to connect to. Either 'public_ips' (default)
    or 'private_ips'.
    '''
    return vm_.get(
        'ssh_interface', __opts__.get('AWS.ssh_interface', 'public_ips')
    )


def get_location(vm_=None):
    '''
    Return the AWS region to use, in this order:
        - CLI parameter
        - Cloud profile setting
        - Global salt-cloud config
    '''
    if __opts__['location'] != '':
        return __opts__['location']
    elif vm_ is not None and 'location' in vm_:
        return vm_['location']
    else:
        return __opts__.get('AWS.location', DEFAULT_LOCATION)


def get_availability_zone(conn, vm_):
    '''
    Return the availability zone to use
    '''
    locations = conn.list_locations()
    avz = None
    if 'availability_zone' in vm_:
        avz = vm_['availability_zone']
    elif 'AWS.availability_zone' in __opts__:
        avz = __opts__['AWS.availability_zone']

    if avz is None:
        # Default to first zone
        return locations[0]
    for loc in locations:
        if loc.availability_zone.name == avz:
            return loc


def create(vm_):
    '''
    Create a single VM from a data dict
    '''
    location = get_location(vm_)
    log.info('Creating Cloud VM {0} in {1}'.format(vm_['name'], location))
    conn = get_conn(location=location)
    usernames = ssh_username(vm_)
    kwargs = {'ssh_key': __opts__['AWS.private_key']}
    kwargs['name'] = vm_['name']
    kwargs['image'] = get_image(conn, vm_)
    kwargs['size'] = get_size(conn, vm_)
    kwargs['location'] = get_availability_zone(conn, vm_)
    ex_keyname = keyname(vm_)
    if ex_keyname:
        kwargs['ex_keyname'] = ex_keyname
    ex_securitygroup = securitygroup(vm_)
    if ex_securitygroup:
        kwargs['ex_securitygroup'] = ex_securitygroup

    try:
        data = conn.create_node(**kwargs)
    except Exception as exc:
        err = (
            'Error creating {0} on AWS\n\n'
            'The following exception was thrown by libcloud when trying to '
            'run the initial deployment: \n{1}').format(
                vm_['name'], exc
        )
        sys.stderr.write(err)
        log.error(err)
        return False

    log.info('Created node {0}'.format(vm_['name']))
    waiting_for_ip = 0
    failures = 0
    while True:
        time.sleep(0.5)
        waiting_for_ip += 1
        data = get_node(conn, vm_['name'])
        if data is None:
            failures += 1
            if failures > 3:
                log.error('Failed to get node data after 3 attempts')
                return False
            log.info(
                'Failed to get node data. Attempts: {0}'.format(
                    failures
                )
            )
            continue
        failures = 0
        if data.public_ips:
            break
        log.warn('Salt node waiting_for_ip {0}'.format(waiting_for_ip))
    if ssh_interface(vm_) == "private_ips":
        log.info('Salt node data. Private_ip: {0}'.format(data.private_ips[0]))
        ip_address = data.private_ips[0]
    else:
        log.info('Salt node data. Public_ip: {0}'.format(data.public_ips[0]))
        ip_address = data.public_ips[0]
    if saltcloud.utils.wait_for_ssh(ip_address):
        for user in usernames:
            if saltcloud.utils.wait_for_passwd(
                    host=ip_address, username=user, ssh_timeout=60,
                    key_filename=__opts__['AWS.private_key']):
                username = user
                break

    sudo = True
    if 'sudo' in vm_.keys():
        sudo = vm_['sudo']

    if __opts__['deploy'] is True:
        deploy_script = script(vm_)
        deploy_kwargs = {
            'host': ip_address,
            'username': username,
            'key_filename': __opts__['AWS.private_key'],
            'deploy_command': 'bash /tmp/deploy.sh',
            'tty': True,
            'script': deploy_script.script,
            'name': vm_['name'],
            'sudo': sudo,
            'start_action': __opts__['start_action'],
            'conf_file': __opts__['conf_file'],
            'sock_dir': __opts__['sock_dir'],
            'minion_pem': vm_['priv_key'],
            'minion_pub': vm_['pub_key'],
            'keep_tmp': __opts__['keep_tmp'],
        }
        deploy_kwargs['minion_conf'] = saltcloud.utils.minion_conf_string(
            __opts__, vm_
        )

        if 'script_args' in vm_:
            deploy_kwargs['script_args'] = vm_['script_args']

        # Deploy salt-master files, if necessary
        if 'make_master' in vm_ and vm_['make_master'] is True:
            deploy_kwargs['master_pub'] = vm_['master_pub']
            deploy_kwargs['master_pem'] = vm_['master_pem']
            master_conf = saltcloud.utils.master_conf_string(__opts__, vm_)
            if master_conf:
                deploy_kwargs['master_conf'] = master_conf

        if username == 'root':
            deploy_kwargs['deploy_command'] = '/tmp/deploy.sh'

        deployed = saltcloud.utils.deploy_script(**deploy_kwargs)
        if deployed:
            log.info('Salt installed on {name}'.format(**vm_))
        else:
            log.error('Failed to start Salt on Cloud VM {name}'.format(**vm_))

    log.info(
        'Created Cloud VM {name} with the following values:'.format(**vm_)
    )
    ret = {}
    for key, val in data.__dict__.items():
        ret[key] = val
        log.debug('  {0}: {1}'.format(key, val))
    volumes = vm_.get('map_volumes')
    if volumes:
        log.info('Create and attach volumes to node {0}'.format(data.name))
        create_attach_volumes(volumes, location, data)

    return ret


def create_attach_volumes(volumes, location, data):
    '''
    Create and attach volumes to created node
    '''
    conn = get_conn(location=location)
    node_avz = data.__dict__.get('extra').get('availability')
    avz = None
    for avz in conn.list_locations():
        if avz.availability_zone.name == node_avz:
            break
    for volume in volumes:
        volume_name = '{0} on {1}'.format(volume['device'], data.name)
        created_volume = conn.create_volume(volume['size'], volume_name, avz)
        attach = conn.attach_volume(data, created_volume, volume['device'])
        if attach:
            log.info(
                '{0} attached to {1} (aka {2}) as device {3}'.format(
                    created_volume.id, data.id, data.name, volume['device']
                )
            )


def stop(name, call=None):
    '''
    Stop a node
    '''
    data = {}

    if call != 'action':
        print('This action must be called with -a or --action.')
        sys.exit(1)

    location = get_location()
    conn = get_conn(location=location)
    node = get_node(conn, name)
    try:
        data = conn.ex_stop_node(node=node)
        log.debug(data)
        log.info('Stopped node {0}'.format(name))
    except Exception as exc:
        log.error('Failed to stop node {0}'.format(name))
        log.error(exc)

    return data


def start(name, call=None):
    '''
    Start a node
    '''
    data = {}

    if call != 'action':
        print('This action must be called with -a or --action.')
        sys.exit(1)

    location = get_location()
    conn = get_conn(location=location)
    node = get_node(conn, name)
    try:
        data = conn.ex_start_node(node=node)
        log.debug(data)
        log.info('Started node {0}'.format(name))
    except Exception as exc:
        log.error('Failed to start node {0}'.format(name))
        log.error(exc)

    return data


def set_tags(name, tags, call=None):
    '''
    Set tags for a node

    CLI Example::

        salt-cloud -a set_tags mymachine tag1=somestuff tag2='Other stuff'
    '''
    if call != 'action':
        print('This action must be called with -a or --action.')
        sys.exit(1)

    location = get_location()
    conn = get_conn(location=location)
    node = get_node(conn, name)
    try:
        log.info('Setting tags for {0}'.format(name))
        conn.ex_create_tags(resource=node, tags=tags)

        # print the new tags- with special handling for renaming of a node
        if 'Name' in tags:
            return get_tags(tags['Name'])
        else:
            return get_tags(name)
    except Exception as exc:
        log.error('Failed to set tags for {0}'.format(name))
        log.error(exc)


def get_tags(name, call=None):
    '''
    Retrieve tags for a node
    '''
    data = {}

    if call != 'action':
        print('This action must be called with -a or --action.')
        sys.exit(1)

    location = get_location()
    conn = get_conn(location=location)
    node = get_node(conn, name)
    try:
        log.info('Retrieving tags from {0}'.format(name))
        data = conn.ex_describe_tags(resource=node)
        log.info(data)
    except Exception as exc:
        log.error('Failed to retrieve tags from {0}'.format(name))
        log.error(exc)

    return data


def del_tags(name, kwargs, call=None):
    '''
    Delete tags for a node

    CLI Example::

        salt-cloud -a del_tags mymachine tag1,tag2,tag3
    '''
    ret = {}

    if call != 'action':
        print('This action must be called with -a or --action.')
        sys.exit(1)

    location = get_location()
    conn = get_conn(location=location)
    node = get_node(conn, name)
    current_tags = conn.ex_describe_tags(resource=node)

    tags = {}
    for tag in kwargs['tags'].split(','):
        tags[tag] = current_tags[tag]

    try:
        conn.ex_delete_tags(resource=node, tags=tags)
        log.info('Deleting tags from {0}'.format(name))
        ret = get_tags(name)
    except Exception as exc:
        log.error('Failed to delete tags from {0}'.format(name))
        log.error(exc)

    return ret


def rename(name, kwargs, call=None):
    '''
    Properly rename a node. Pass in the new name as "new name".

    CLI Example::

        salt-cloud -a rename mymachine newname=yourmachine
    '''
    if call != 'action':
        print('This action must be called with -a or --action.')
        sys.exit(1)

    location = get_location()
    conn = get_conn(location=location)
    node = get_node(conn, name)
    tags = {'Name': kwargs['newname']}
    try:
        log.info('Renaming {0} to {1}'.format(name, kwargs['newname']))
        conn.ex_create_tags(resource=node, tags=tags)
        saltcloud.utils.rename_key(
            __opts__['pki_dir'], name, kwargs['newname']
        )
    except Exception as exc:
        log.error(
            'Failed to rename {0} to {1}'.format(
                name, kwargs['newname']
            )
        )
        log.error(exc)


def destroy(name):
    '''
    Wrap core libcloudfuncs destroy method, adding check for termination
    protection
    '''
    ret = {}

    from saltcloud.libcloudfuncs import destroy as libcloudfuncs_destroy
    location = get_location()
    conn = get_conn(location=location)
    libcloudfuncs_destroy = namespaced_function(libcloudfuncs_destroy, globals(), (conn,))
    try:
        result = libcloudfuncs_destroy(name, conn)
        ret[name] = result
    except Exception as e:
        if e.message.startswith('OperationNotPermitted'):
            log.info('Failed: termination protection is enabled on {0}'.format(name))
        else:
            raise e

    return ret

