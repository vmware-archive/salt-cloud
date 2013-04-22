'''

    libcloud joyent driver exension

'''
# import libcloud common libraries/methods
from saltcloud.libcloudfuncs import *
import urllib

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


    def __post_request(self,url,data=""):
        result = self.connection.request(url,data=data,method='POST') 
        return result.status == httplib.ACCEPTED

    def __get_request(self,url):
        result = self.connection.request(url,method='GET') 
        return result.status == httplib.ACCEPTED

    def __delete_request(self,url):
        result = self.connection.request(url,method='DELETE') 
        return result.status == httplib.ACCEPTED

    def sc_start_node(self,node):
        """
        start node

        @param  node: The node to be started
        @type   node: L{Node}

        @rtype: C{bool}
        """
        data = json.dumps({'action': 'start'})
        return self.__post_request('/my/machines/%s' % (node.id),data)

    def sc_create_node_snapshot(self, node, name):
        data = json.dumps({'name': name })
        return self.__post_request('/my/machines/%s/snapshots' % (node.id), data)

    def sc_start_node_snapshot(self, node, name):
        return self.__post_request('/my/machines/%s/snapshots/%s' % (node.id,name))

    def sc_list_snapshots(self, node):
        return self.__get_request('/my/machines/%s/snapshots' % (node.id,name))

    def sc_get_node_snapshot(self, node, name):
        return self.__get_request('/my/machines/%s/snapshots/%s' % (node.id,name))

    def sc_del_node_snapshot(self, node, name):
        return self.connection.request('/my/machines/%s/snapshots/%s' % (node.id,name))

    def sc_update_node_metadata(self,node,key,value):
        data = json.dumps({key: value})
        return self.__post_request('/my/machines/%s/metadata' % (node.id), data)

    def sc_get_node_metadata(self,node):
        return self.__get_request('/my/machines/%s/metadata' % (node.id))

    def sc_del_node_metadata(self,node,key):
        return self.__delete_request('/my/machines/%s/metadata/%s' % (node.id,key))

    def sc_del_all_node_metadata(self,node):
        return self.__delete_request('/my/machines/%s/metadata' % (node.id))

    def sc_update_node_tags(self,node, kvps):
        data = urllib.urlencode(kvps)
        return self.__post_request('/my/machines/%s/tags' % (node.id), data)

    def sc_get_node_tags(self,node):
        return self.__get_request('/my/machines/%s/tags' % (node.id))
    
    def sc_get_node_tag(self,node,tag):
        return self.__get_request('/my/machines/%s/tags/%s' % (node.id,tag))

    def sc_del_node_tag(self,node,key):
        return self.__delete_request('/my/machines/%s/tags/%s' % (node.id,key))

    def sc_del_all_node_tags(self,node):
        return self.__delete_request('/my/machines/%s/tags' % (node.id))

    def sc_describe_analytics(self):
        return self.__get_request('/my/machines/analytics')

    def sc_list_instrumenations(self):
        return self.__get_request('/my/machines/analytics/instrumentations')

    def sc_get_instrumentation(self,id):
        return self.__get_request("/my/machines/analytics/instrumentations/{0}".format(id))

    def sc_get_instrumentationValue(self,id):
        return self.__get_request(
                "/my/machines/analytics/instrumentations/{0}/value/raw".format(id))

    def sc_get_instrumentationHeatmap(self,id):
        return self.__get_request(
                "/my/machines/analytics/instrumentations/{0}/value/heatmap/image".format(id))

    def sc_get_instrumentationHeatmapDetails(self,id):
        return self.__get_request(
                "/my/machines/analytics/instrumentations/{0}/value/heatmap/details".format(id))

    def sc_create_instrumentation(self,kvps):
        data = urllib.urlencode(kvps)
        return self.__post_request(
                "/my/machines/analytics/instrumentations".format(id), 
                data)

    def sc_del_instrumentation(self,id):
        return self.__delete_request('/my/machines/instrumentations/{0}'.format(node.id))

    def sc_list_ssh_keys(self):
        return self.__get_request("/my/machines/keys")

    def sc_get_key(self,keyname):
        return self.__get_request("/my/machines/%s" % keyname )

    def sc_create_key(self,keyname,key):
        data = json.dumps({'name': keyname, 'key':key })
        return self.__post_request("/my/machines/keys", data)

    def sc_delete_key(self,keyname):
        return self.__delete_request("/my/machines/keys/%s" % keyname)

    def sc_list_datacenters(self):
        return self.__get_request("/my/machines/datacenters")

    def sc_get_datacenter(self,dc):
        return self.__get_request("/my/machines/datacenters/%s" % dc)

