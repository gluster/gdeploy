"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Global
import re

def ctdb_start(section_dict):
    section_dict['service'] = ['ctdb']
    section_dict['state'] = 'started'
    return section_dict, defaults.SERVICE_MGMT

def ctdb_stop(section_dict):
    section_dict['service'] = ['ctdb']
    section_dict['state'] = 'stopped'
    return section_dict, defaults.SERVICE_MGMT

def ctdb_enable(section_dict):
    section_dict['service'] = ['ctdb']
    section_dict['enabled'] = 'yes'
    return section_dict, defaults.CHKCONFIG

def ctdb_disable(section_dict):
    section_dict['service'] = ['ctdb']
    section_dict['enabled'] = 'no'
    return section_dict, defaults.CHKCONFIG

def ctdb_setup(section_dict):
    section_dict['nodes'] = '\n'.join(sorted(set(Global.hosts)))
    paddress = section_dict.get('public_address')
    ctdbnodes = section_dict.get('ctdb_nodes')

    if paddress:
        if not isinstance(paddress, list):
            paddress= [paddress]
        paddress_list = map(lambda x: x.split(' '), paddress)
        paddress_list = filter(None, paddress_list)
        addresses, interfaces = [], []
        for ip in paddress_list:
            addresses.append(ip[0])
            try:
                interfaces.append(ip[1])
            except:
                interfaces.append(' ')
        interfaces = map(lambda x: x.replace(';',','), interfaces)
        paddress = []
        for ip, inter in zip(addresses, interfaces):
            public_add = ip + ' ' + inter
            paddress.append(public_add)
        section_dict['paddress'] = '\n'.join(paddress)

    if ctdbnodes:
        # If there is a single item listify it
        if not isinstance(ctdbnodes, list):
            ctdbnodes = [ctdbnodes]
        section_dict['ctdbnodes'] = "\n".join(ctdbnodes)
    section_dict, enable_yml = ctdb_enable(section_dict)
    section_dict, start_yml = ctdb_start(section_dict)

    yaml_list = [defaults.CTDB_SETUP, defaults.VOLSTOP_YML,
                 defaults.VOLUMESTART_YML, enable_yml, start_yml,
                 defaults.SMB_FOR_CTDB]

    return section_dict, yaml_list
