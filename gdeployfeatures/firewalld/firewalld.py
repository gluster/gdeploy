"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults
from gdeploylib import Global

def firewalld_add(section_dict):
    section_dict['firewall_state'] = 'enabled'
    return get_yml_lists(section_dict)

def firewalld_delete(section_dict):
    section_dict['firewall_state'] = 'disabled'
    return get_yml_lists(section_dict)


def  get_yml_lists(section_dict):
    ymls = {'ports': defaults.PORT_OP,
            'services': defaults.SERVICE_OP
            }
    yml_list = [v for k,v in ymls.iteritems() if section_dict[k]]
    if Global.trace:
    	for ymll in yml_list:
    		Global.logger.info("Executing %s."%ymll)
    return section_dict, yml_list
