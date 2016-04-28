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
    if filename:
        section_dict['filename'] = filename
    else:
        hostnames = helpers.listify(section_dict.get("hostnames"))
        zone = helpers.listify(section_dict.get("zone"))
        devices = helpers.listify(section_dict.get("devices"))
        if not (hostnames and zone and devices):
            return section_dict, None
        section_dict = get_hostnames(section_dict, hostnames, zone,
                devices)

    if not Global.server or Global.port:
        section_dict = get_server_name(section_dict)
    return section_dict, defaults.HKT_LOAD_TOPO

def get_hostnames(section_dict, hostnames, zone, devices):
    global helpers
    if len(hostnames) != len(zone) or len(zone) != len(devices):
        print "Error: Entity number mismatch"
        helpers.cleanup_and_quit()
    data = []
    for hosts, zone, devs in zip(hostnames, zone, devices):
        hdict = {}
        h = hosts.split(';')
        manage = ''
        storage = ''
        for each in h:
            mgroup = re.match('manage=(.*)', each)
            if mgroup:
                manage = mgroup.group(1)
            sgroup = re.match('storage=(.*)', each)
            if sgroup:
                storage = sgroup.group(1)
        hdict["manage"] = h[0] if not manage else manage
        hdict["storage"] = h[-1] if not storage else storage
        devnames = devs.split(';')
        if devnames:
            hdict["devices"] = helpers.correct_brick_format(devnames)
        else:
            hdict["devices"] = ''
        hdict["zone"] = zone
        data.append(hdict)
    section_dict['hdict'] = data
    return section_dict


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
    section_dict["servername"] = "http://{0}:{1}".format(server, port)
    return section_dict

