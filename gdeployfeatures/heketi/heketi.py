#!/usr/bin/python
"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Global, Helpers
import re

helpers = Helpers()

def heketi_heketi_init(section_dict):
    yamls = []
    get_server_name(section_dict)
    section_dict['port'] = Global.port
    section_dict['server'] = Global.server
    yamls.append(defaults.HKT_CONFIG_COPY)
    section_dict['service'] = 'heketi'
    section_dict['state'] = 'started'
    section_dict['enabled'] = 'yes'
    yamls.append(defaults.CHKCONFIG)
    yamls.append(defaults.SERVICE_MGMT)

    section_dict, ymls = heketi_load_topology(section_dict)
    if ymls:
        yamls.append(ymls)
    return section_dict, yamls


def heketi_load_topology(section_dict):
    filename = section_dict.get('topologyfile')
    section_dict['filename'] = filename
    topo = section_dict.get('load_topology')
    if not filename and topo.lower() == 'false':
        return section_dict, None

    if not Global.server or Global.port:
        get_server_name(section_dict)
    return section_dict, defaults.HKT_LOAD_TOPO

def get_server_name(section_dict):
    global helpers
    try:
        server = section_dict.get('server') or Global.hosts[0]
    except:
        print "Error: Heketi server name or IP not provided"
        helpers.cleanup_and_quit()
    server_group = re.match('(.*):(.*)', server)
    if not server_group:
        port = section_dict.get('port')
    else:
        server = server_group.group(1)
        port = server_group.group(2)
    Global.server = server
    Global.port = port
    return

