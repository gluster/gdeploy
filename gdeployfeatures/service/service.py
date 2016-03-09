#!/usr/bin/python
"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults

def service_start(section_dict):
    section_dict['state'] = 'started'
    return section_dict, defaults.SERVICE_MGMT

def service_stop(section_dict):
    section_dict['state'] = 'stopped'
    return section_dict, defaults.SERVICE_MGMT

def service_restart(section_dict):
    section_dict['state'] = 'restarted'
    return section_dict, defaults.SERVICE_MGMT

def service_reload(section_dict):
    section_dict['state'] = 'reloaded'
    return section_dict, defaults.SERVICE_MGMT

def service_enable(section_dict):
    section_dict['enabled'] = 'yes'
    return section_dict, defaults.CHKCONFIG

def service_disable(section_dict):
    section_dict['enabled'] = 'no'
    return section_dict, defaults.CHKCONFIG
