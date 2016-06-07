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
    option = ''
    pattern = '^CTDB_.*'
    opt_matches = [opt for opt in list(section_dict) if
            re.search(pattern, opt)]
    for key in opt_matches:
        if section_dict[key] and section_dict[key].lower() != 'none':
            option += key + '=' + str(section_dict[key]) + '\n'

    section_dict['options'] = option
    section_dict['nodes'] = '\n'.join(Global.hosts)
    paddress = section_dict.get('public_address')
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
    section_dict, enable_yml = ctdb_enable(section_dict)
    section_dict, start_yml = ctdb_start(section_dict)
    return section_dict, [defaults.CTDB_SETUP, enable_yml, start_yml]
