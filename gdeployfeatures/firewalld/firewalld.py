"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Global

def firewalld_add(section_dict):
    section_dict['firewall_state'] = 'enabled'
    Global.logger.info("Enabling firewalld service")
    return get_yml_lists(section_dict)

def firewalld_delete(section_dict):
    section_dict['firewall_state'] = 'disabled'
    Global.logger.info("Disabling firewalld service")
    return get_yml_lists(section_dict)


def  get_yml_lists(section_dict):
    ymls = {'ports': defaults.PORT_OP,
            'services': defaults.SERVICE_OP
            }
    yml_list = [v for k,v in ymls.items() if section_dict[k]]
    return section_dict, yml_list
