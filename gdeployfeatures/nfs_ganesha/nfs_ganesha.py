#!/usr/bin/python
"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Helpers, Global

helpers = Helpers()

def nfs_ganesha_create_cluster(section_dict):
    global helpers
    cluster_nodes = get_cluster_nodes(section_dict)
    section_dict['ha_name'] = section_dict.pop('ha-name')
    if not len(cluster_nodes) == len(section_dict.get('vip')):
            print "\nError: Provide virtual IPs for all the hosts in "\
                    "the cluster-nodes"
            helpers.cleanup_and_quit()
    section_dict['vip'] = get_host_vips(cluster_nodes)
    section_dict['value'] = "on"
    ymls = [ defaults.GANESHA_BOOTSTRAP, defaults.GANESHA_PUBKEY,
            defaults.COPY_SSH, defaults.SET_AUTH_PASS, defaults.PCS_AUTH,
            defaults.SHARED_MOUNT, defaults.GANESHA_CONF_CREATE,
            defaults.ENABLE_GANESHA, defaults.GANESHA_VOL_CONFS,
            defaults.GANESHA_VOL_EXPORT ]
    return section_dict, ymls

def nfs_ganesha_destroy_cluster(section_dict):
    return section_dict, defaults.GANESHA_DISABLE

def nfs_ganesha_add_node(section_dict):
    new_nodes = section_dict.get('nodes')
    vips = get_host_vips(new_nodes)
    data = []
    for node, vip in zip(new_nodes, vips):
        nodes_list = {}
        nodes_list['host'] = node
        nodes_list['vip'] = vip
        data.append(nodes_list)
    section_dict['nodes_list'] = data
    return section_dict, [defaults.GANESHA_BOOTSTRAP,
                                defaults.GANESHA_ADD_NODE]

def nfs_ganesha_delete_node(section_dict):
    return section_dict, defaults.GANESHA_DELETE_NODE

def nfs_ganesha_export_volume(section_dict):
    section_dict['value'] = "on"
    return section_dict, [defaults.GANESHA_VOL_CONFS,
            defaults.GANESHA_VOL_EXPORT ]

def nfs_ganesha_unexport_volume(section_dict):
    section_dict['value'] = "off"
    return section_dict, defaults.GANESHA_VOL_EXPORT

def get_cluster_nodes(section_dict):
    global helpers
    cluster_nodes = section_dict.get('client-nodes')
    if Global.hosts:
        if not set(cluster_nodes).issubset(set(Global.hosts)):
            print "\nError: cluster-nodes are not subset of the 'hosts' "\
                    "provided"
            helpers.cleanup_and_quit()
    else:
        Global.hosts = cluster_nodes
    helpers.write_to_inventory('cluster_nodes', cluster_nodes)
    helpers.write_to_inventory('master_node', [cluster_nodes[0]])
    section_dict['cluster_nodes'] = ','.join(node for node in cluster_nodes)
    section_dict['master_node'] = cluster_nodes[0]
    return cluster_nodes

def get_host_vips(self, cluster):
    VIPs = section_dict.get('vip')
    if len(cluster) != len(VIPs):
        print "\nError: The number of cluster_nodes provided and VIP "\
                "given doesn't match. Exiting!"
        self.cleanup_and_quit()
    vip_list = []
    for host, vip in zip(cluster, VIPs):
        key = 'VIP_' + host
        vip_list.append("%s=\"%s\"" %(key, vip))
    VIPs = '\n'.join(vip_list)
    return VIPs

