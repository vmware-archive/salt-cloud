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
import types
import time
import tempfile
import subprocess

# Import libcloud
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import MultiStepDeployment, ScriptDeployment, SSHKeyDeployment

# Import salt libs
import saltcloud.utils
from saltcloud.libcloudfuncs import *

# Import paramiko
import paramiko

# Init the libcloud functions
avail_images = types.FunctionType(avail_images.__code__, globals())
avail_sizes = types.FunctionType(avail_sizes.__code__, globals())
script = types.FunctionType(script.__code__, globals())
destroy = types.FunctionType(destroy.__code__, globals())
list_nodes = types.FunctionType(list_nodes.__code__, globals())


# Only load in this module if the AWS configurations are in place
def __virtual__():
    '''
    Set up the libcloud funcstions and check for AWS configs
    '''
    confs = [
            'AWS.id',
            'AWS.key',
            'AWS.keyname',
            'AWS.securitygroup',
            'AWS.private_key',
            ]
    for conf in confs:
        if conf not in __opts__:
            return False
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


def get_conn(**kwargs):
    '''
    Return a conn object for the passed vm data
    '''
    if 'location' in kwargs:
        location = kwargs['location']
        if location not in EC2_LOCATIONS:
            return None     #TODO raise exception
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
    return str(vm_.get('AWS.keyname', __opts__.get('AWS.keyname', '')))


def securitygroup(vm_):
    '''
    Return the security group
    '''
    return str(vm_.get('AWS.securitygroup', __opts__.get('AWS.securitygroup', 'default')))


def ssh_username(vm_):
    '''
    Return the ssh_username. Defaults to 'ec2-user'.
    '''
    return vm_.get('ssh_username', __opts__.get('AWS.ssh_username', 'ec2-user'))


def ssh_interface(vm_):
    '''
    Return the ssh_interface type to connect to. Either 'public_ips' (default) or 'private_ips'.
    '''
    return vm_.get('ssh_interface', __opts__.get('AWS.ssh_interface', 'public_ips'))


def get_location(vm_):
    '''
    Return the AWS region to use
    '''
    return vm_.get('location', __opts__.get('AWS.location', DEFAULT_LOCATION))


def get_availability_zone(conn, vm_):
    '''
    Return the availability zone to use
    '''
    locations = conn.list_locations()
    az = None
    if 'availability_zone' in vm_:
        az = vm_['availability_zone']
    elif 'EC2.availability_zone' in __opts__:
        az = __opts__['EC2.availability_zone']

    if az is None:
        # Default to first zone
        return locations[0]
    for loc in locations:
        if loc.availability_zone.name == az:
            return loc


def create(vm_):
    '''
    Create a single vm from a data dict
    '''
    location = get_location(vm_)
    print('Creating Cloud VM {0} in {1}'.format(vm_['name'], location))
    conn = get_conn(location=location)
    kwargs = {'ssh_username': ssh_username(vm_),
              'ssh_key': __opts__['AWS.private_key']}
    kwargs['name'] = vm_['name']
    deploy_script = script(vm_)
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
        err = ('Error creating {0} on AWS\n\n'
               'The following exception was thrown by libcloud when trying to '
               'run the initial deployment: \n{1}').format(
                       vm_['name'], exc
                       )
        sys.stderr.write(err)
        return False
    while not data.public_ips:
        time.sleep(0.5)
        data = get_node(conn, vm_['name'])
    if ssh_interface(vm_) == "private_ips":
        ip_address = data.private_ips[0]
    else:
        ip_address = data.public_ips[0]
    if saltcloud.utils.wait_for_ssh(ip_address):
        fd_, path = tempfile.mkstemp()
        os.close(fd_)
        with open(path, 'w+') as fp_:
            fp_.write(deploy_script.script)
        cmd = ('scp -oStrictHostKeyChecking=no -i {0} {3} {1}@{2}:/tmp/deploy.sh ').format(
                       __opts__['AWS.private_key'],
                       kwargs['ssh_username'],
                       ip_address,
                       path,
                       )
        if subprocess.call(cmd, shell=True) != 0:
            time.sleep(15)
            cmd = ('scp -oStrictHostKeyChecking=no -i {0} {3} {1}@{2}:/tmp/deploy.sh ').format(
                       __opts__['AWS.private_key'],
                       'root',
                       ip_address,
                       path,
                       )
            subprocess.call(cmd, shell=True)
            cmd = ('ssh -oStrictHostKeyChecking=no -t -i {0} {1}@{2} '
                   '"sudo bash /tmp/deploy.sh"').format(
                       __opts__['AWS.private_key'],
                       'root',
                       ip_address,
                       )
        else:
            cmd = ('ssh -oStrictHostKeyChecking=no -t -i {0} {1}@{2} '
                   '"sudo bash /tmp/deploy.sh"').format(
                       __opts__['AWS.private_key'],
                       kwargs['ssh_username'],
                       ip_address,
                       )
        subprocess.call(cmd, shell=True)
        os.remove(path)
    print('Created Cloud VM {0} with the following values:'.format(
        vm_['name']
        ))
    for key, val in data.__dict__.items():
        print('  {0}: {1}'.format(key, val))
