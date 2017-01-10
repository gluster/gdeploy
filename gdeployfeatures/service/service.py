"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults
from gdeploylib import Global

def service_start(section_dict):
    section_dict['state'] = 'started'
    slice_setup = section_dict.get('slice_setup')
    if slice_setup.lower() == 'yes':
        return setup_slice(section_dict)
    if Global.trace:
        Global.logger.info("Executing %s."%defaults.SERVICE_MGMT)
    return section_dict, defaults.SERVICE_MGMT

def service_stop(section_dict):
    section_dict['state'] = 'stopped'
    if Global.trace:
        Global.logger.info("Executing %s."%defaults.SERVICE_MGMT)
    return section_dict, defaults.SERVICE_MGMT

def service_restart(section_dict):
    section_dict['state'] = 'restarted'
    slice_setup = section_dict.get('slice_setup')
    if slice_setup.lower() == 'yes':
        return setup_slice(section_dict)
    if Global.trace:
        Global.logger.info("Executing %s."%defaults.SERVICE_MGMT)
    return section_dict, defaults.SERVICE_MGMT

def service_reload(section_dict):
    section_dict['state'] = 'reloaded'
    if Global.trace:
        Global.logger.info("Executing %s."%defaults.SERVICE_MGMT)
    return section_dict, defaults.SERVICE_MGMT

def service_enable(section_dict):
    section_dict['enabled'] = 'yes'
    if Global.trace:
        Global.logger.info("Executing %s."%defaults.CHKCONFIG)
    return section_dict, defaults.CHKCONFIG

def service_disable(section_dict):
    section_dict['enabled'] = 'no'
    if Global.trace:
        Global.logger.info("Executing %s."%defaults.CHKCONFIG)
    return section_dict, defaults.CHKCONFIG

def setup_slice(section_dict):
    service = section_dict.get('service')
    yamls = defaults.SERVICE_MGMT
    if service == 'glusterd':
        yamls = [defaults.SLICE_SETUP, defaults.SERVICE_MGMT]
    else:
        print "Slice setup is currently limited to glusterd."
        print "Ignoring slice setup"
    if Global.trace:
        for ymll in yamls:
            Global.logger.info("Executing %s."%ymll)
    return section_dict, yamls

