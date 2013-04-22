'''

    libcloud joyent driver exension

'''
# import libcloud common libraries/methods
from saltcloud.libcloudfuncs import *

# import joyent sepcific driver classes
from libcloud.compute.drivers.joyent import (
    JoyentNodeDriver,
    JoyentConnection,
    JoyentResponse
    )


class ExtendedJoyentNodeDriver(JoyentNodeDriver):
    """
    Extended Joyent node driver class.
    """

    def __init__(self,*args,**kwargs):
        super(ExtendedJoyentNodeDriver,self).__init__(*args,**kwargs)



    def sc_start_node(self,node):
        """
        start node

        @param  node: The node to be started
        @type   node: L{Node}

        @rtype: C{bool}
        """
        data = json.dumps({'action': 'start'})
        result = self.connection.request('/my/machines/%s' % (node.id), 
                data=data, method='POST')
        return result.status == httplib.ACCEPTED
