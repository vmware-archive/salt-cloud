'''
Digital Ocean Cloud Module
==========================

The Digital Ocean cloud module is used to control access to the Digital Ocean
VPS system.

Use of this module only requires the ``api_key`` parameter to be set. Using the
old cloud providers configuration syntax, in the main cloud configuration
file:

.. code-block:: yaml

    # Digital Ocean account keys
    DIGITAL_OCEAN.client_key: wFGEwgregeqw3435gDger
    DIGITAL_OCEAN.api_key: GDE43t43REGTrkilg43934t34qT43t4dgegerGEgg


Using the new format, set up the cloud configuration at
 ``/etc/salt/cloud.providers`` or
 ``/etc/salt/cloud.providers.d/digital_ocean.conf``:

.. code-block:: yaml

    my-digital-ocean-config:
      # Digital Ocean account keys
      client_key: wFGEwgregeqw3435gDger
      api_key: GDE43t43REGTrkilg43934t34qT43t4dgegerGEgg
      provider: digital_ocean

'''

# Import python libs
import time
import json
import urllib
import urllib2
import logging

# Import salt cloud libs
import saltcloud.utils
import saltcloud.config as config
from saltcloud.exceptions import SaltCloudNotFound, SaltCloudSystemExit

# Get logging started
log = logging.getLogger(__name__)


# Only load in this module if the DIGITAL_OCEAN configurations are in place
def __virtual__():
    '''
    Check for Digital Ocean configurations
    '''
    if get_configured_provider() is False:
        log.debug(
            'There is no Digital Ocean cloud provider configuration '
            'available. Not loading module.'
        )
        return False

    log.debug('Loading Digital Ocean cloud module')
    return 'digital_ocean'


def get_configured_provider():
    '''
    Return the first configured instance.
    '''
    return config.is_provider_configured(
        __opts__, 'digital_ocean', ('api_key',)
    )


def avail_locations():
    '''
    Return a dict of all available VM locations on the cloud provider with
    relevant data
    '''
    items = query(method='regions')
    ret = {}
    for region in items['regions']:
        ret[region['name']] = {}
        for item in region.keys():
            ret[region['name']][item] = str(region[item])

    return ret


def avail_images():
    '''
    Return a list of the images that are on the provider
    '''
    items = query(method='images')
    ret = {}
    for image in items['images']:
        ret[image['name']] = {}
        for item in image.keys():
            ret[image['name']][item] = str(image[item])

    return ret


def avail_sizes():
    '''
    Return a list of the image sizes that are on the provider
    '''
    items = query(method='sizes')
    ret = {}
    for size in items['sizes']:
        ret[size['name']] = {}
        for item in size.keys():
            ret[size['name']][item] = str(size[item])

    return ret


def list_nodes():
    '''
    Return a list of the VMs that are on the provider
    '''
    items = query(method='droplets')

    ret = {}
    for node in items['droplets']:
        ret[node['name']] = {
            'id': node['id'],
            'image_id': node['image_id'],
            'public_ips': str(node['ip_address']),
            'size_id': node['size_id'],
            'status': str(node['status']),
        }
    return ret


def list_nodes_full():
    '''
    Return a list of the VMs that are on the provider
    '''
    items = query(method='droplets')

    ret = {}
    for node in items['droplets']:
        ret[node['name']] = {}
        for item in node.keys():
            ret[node['name']][item] = str(node[item])
    return ret


def list_nodes_select():
    '''
    Return a list of the VMs that are on the provider
    '''
    items = query(method='droplets')

    ret = {}
    for node in items['droplets']:
        ret[node['name']] = {}
        for item in node.keys():
            if str(item) in __opts__['query.selection']:
                ret[node['name']][item] = str(node[item])
    return ret


def get_image(vm_):
    '''
    Return the image object to use
    '''
    images = avail_images()
    vm_image = str(config.get_config_value(
        'image', vm_, __opts__, search_global=False
    ))
    for image in images:
        if vm_image in (images[image]['name'], images[image]['id']):
            return images[image]['id']
    raise SaltCloudNotFound('The specified image could not be found.')


def get_size(vm_):
    '''
    Return the VM's size. Used by create_node().
    '''
    sizes = avail_sizes()
    vm_size = str(config.get_config_value(
        'size', vm_, __opts__, search_global=False
    ))
    for size in sizes:
        if vm_size in (sizes[size]['name'], sizes[size]['id']):
            return sizes[size]['id']
    raise SaltCloudNotFound('The specified size could not be found.')


def get_location(vm_):
    '''
    Return the VM's location
    '''
    locations = avail_locations()
    vm_location = str(config.get_config_value(
        'location', vm_, __opts__, search_global=False
    ))

    for location in locations:
        if vm_location in (locations[location]['name'],
                           locations[location]['id']):
            return locations[location]['id']
    raise SaltCloudNotFound('The specified location could not be found.')


def create_node(args):
    '''
    Create a node
    '''
    node = query(method='droplets', command='new', args=args)
    return node


def create(vm_):
    '''
    Create a single VM from a data dict
    '''
    log.info('Creating Cloud VM {0}'.format(vm_['name']))
    deploy_script = script(vm_)
    kwargs = {
        'name': vm_['name'],
        'size_id': get_size(vm_),
        'image_id': get_image(vm_),
        'region_id': get_location(vm_),
        'ssh_key_ids': get_keyid(
            config.get_config_value(
                'ssh_key_name', vm_, __opts__, search_global=False
            )
        )
    }

    try:
        ret = create_node(kwargs)
    except Exception as exc:
        log.error(
            'Error creating {0} on DIGITAL_OCEAN\n\n'
            'The following exception was thrown when trying to '
            'run the initial deployment: {1}'.format(
                vm_['name'],
                exc.message
            ),
            # Show the traceback if the debug logging level is enabled
            exc_info=log.isEnabledFor(logging.DEBUG)
        )
        return False

    waiting_for_ip = 0
    while 'ip_address' not in data:
        log.debug('Salt node waiting for IP {0}'.format(waiting_for_ip))
        time.sleep(5)
        waiting_for_ip += 1
        data = _get_node(vm_['name'])

    if config.get_config_value('deploy', vm_, __opts__) is True:
        deploy_script = script(vm_)
        deploy_kwargs = {
            'host': data['ip_address'],
            'username': 'root',
            'key_filename': config.get_config_value(
                'ssh_key_file', vm_, __opts__, search_global=False
            ),
            'script': deploy_script,
            'name': vm_['name'],
            'deploy_command': '/tmp/deploy.sh',
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
            __opts__, vm_
        )

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
    return ret


def query(method='droplets', droplet_id=None, command=None, args=None):
    '''
    Make a web call to Digital Ocean
    '''
    path = 'https://api.digitalocean.com/{0}/'.format(method)

    if droplet_id:
        path = '{0}/'.format(droplet_id)

    if command:
        path += command

    if type(args) is not dict:
        args = {}

    args['client_id'] = config.get_config_value(
        'client_key', get_configured_provider(), __opts__, search_global=False
    )
    args['api_key'] = config.get_config_value(
        'api_key', get_configured_provider(), __opts__, search_global=False
    )

    path += '?%s'
    params = urllib.urlencode(args)
    result = urllib2.urlopen(path % params)
    # TODO: Attention to the HTTP Code
    log.debug(result.geturl())
    content = result.read()
    result.close()

    return json.loads(content)


def script(vm_):
    '''
    Return the script deployment object
    '''
    minion = saltcloud.utils.minion_conf_string(__opts__, vm_)
    script = saltcloud.utils.os_script(
        config.get_config_value('script', vm_, __opts__),
        vm_, __opts__, minion,
    )
    return script


def show_instance(name, call=None):
    '''
    Show the details from Digital Ocean concerning a droplet
    '''
    if call != 'action':
        raise SaltCloudSystemExit(
            'The show_instance action must be called with -a or --action.'
        )

    return _get_node(name)


def _get_node(name, location=None):
    attempts = 10
    while attempts >= 0:
        try:
            return list_nodes_full()[name]
        except KeyError:
            attempts -= 1
            log.debug(
                'Failed to get the data for the node {0!r}. Remaining '
                'attempts {1}'.format(
                    name, attempts
                )
            )
            # Just a little delay between attempts...
            time.sleep(0.5)
    return {}


def list_keypairs(call=None):
    '''
    Return a dict of all available VM locations on the cloud provider with
    relevant data
    '''
    if call != 'function':
        log.error(
            'The list_keypairs function must be called with -f or --function.'
        )
        return False

    items = query(method='ssh_keys')
    ret = {}
    for keypair in items['ssh_keys']:
        ret[keypair['name']] = {}
        for item in keypair.keys():
            ret[keypair['name']][item] = str(keypair[item])

    return ret


def show_keypair(kwargs=None, call=None):
    '''
    Show the details of an SSH keypair
    '''
    if call != 'function':
        log.error(
            'The show_keypair function must be called with -f or --function.'
        )
        return False

    if not kwargs:
        kwargs = {}

    if 'keyname' not in kwargs:
        log.error('A keyname is required.')
        return False

    keypairs = list_keypairs(call='function')
    keyid = keypairs[kwargs['keyname']]['id']
    log.debug('Key ID is {0}'.format(keyid))

    details = query(method='ssh_keys', command=keyid)

    return details


def get_keyid(keyname):
    '''
    Return the ID of the keyname
    '''
    keypairs = list_keypairs(call='function')
    keyid = keypairs[keyname]['id']
    if keyid:
        return keyid
    raise SaltCloudNotFound('The specified ssh key could not be found.')


def destroy(name, call=None):
    '''
    Destroy a node. Will check termination protection and warn if enabled.

    CLI Example::

        salt-cloud --destroy mymachine
    '''
    data = show_instance(name, call='action')
    node = query(method='droplets', command='{0}/destroy'.format(data['id']))
    return node
