'''

    libcloud rackspace driver exension

'''
# import libcloud common libraries/methods
from saltcloud.libcloudfuncs import *

# import rackspace sepcific driver classes
from libcloud.compute.drivers.rackspace import (
    RackspaceNodeDriver
    )


class ExtendedRackspaceNodeDriver(RackspaceNodeDriver):
    """
    Extended rackspace node driver class.
    """

    def __init__(self,*args,**kwargs):
        super(ExtendedRackspaceNodeDriver,self).__init__(*args,**kwargs)

