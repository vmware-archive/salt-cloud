'''

    libcloud openstack driver exension

'''
# import libcloud common libraries/methods
from saltcloud.libcloudfuncs import *

# import openstack sepcific driver classes
from libcloud.compute.drivers.openstack import (
    OpenStackNodeDriver
    )


class ExtendedOpenStackNodeDriver(OpenStackNodeDriver):
    """
    Extended openstack node driver class.
    """

    def __init__(self,*args,**kwargs):
        super(ExtendedOpenstackNodeDriver,self).__init__(*args,**kwargs)

