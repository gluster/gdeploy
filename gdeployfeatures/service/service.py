"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Global

def service_start(section_dict):
    section_dict['state'] = 'started'
    slice_setup = section_dict.get('slice_setup')
    Global.ignore_errors = section_dict.get('ignore_service_errors')
    if slice_setup.lower() == 'yes':
        return setup_slice(section_dict)
    Global.logger.info("Starting service %s"%section_dict['service'])
    return section_dict, defaults.SERVICE_MGMT

def service_stop(section_dict):
    section_dict['state'] = 'stopped'
    Global.ignore_errors = section_dict.get('ignore_service_errors')
    Global.logger.info("Stopping service %s"%section_dict['service'])
    return section_dict, defaults.SERVICE_MGMT

def service_restart(section_dict):
    section_dict['state'] = 'restarted'
    slice_setup = section_dict.get('slice_setup')
    Global.ignore_errors = section_dict.get('ignore_service_errors')
    if slice_setup.lower() == 'yes':
        return setup_slice(section_dict)
    Global.logger.info("Restarting service %s"%section_dict['service'])
    return section_dict, defaults.SERVICE_MGMT

def service_reload(section_dict):
    section_dict['state'] = 'reloaded'
    Global.ignore_errors = section_dict.get('ignore_service_errors')
    Global.logger.info("Reloading service %s"%section_dict['service'])
    return section_dict, defaults.SERVICE_MGMT

def service_enable(section_dict):
    section_dict['enabled'] = 'yes'
    Global.ignore_errors = section_dict.get('ignore_service_errors')
    Global.logger.info("Enabling service %s"%section_dict['service'])
    return section_dict, defaults.CHKCONFIG

def service_disable(section_dict):
    section_dict['enabled'] = 'no'
    Global.ignore_errors = section_dict.get('ignore_service_errors')
    Global.logger.info("Disabling service %s"%section_dict['service'])
    return section_dict, defaults.CHKCONFIG

def setup_slice(section_dict):
    service = section_dict.get('service')
    yamls = defaults.SERVICE_MGMT
    if service == 'glusterd':
        yamls = [defaults.SLICE_SETUP, defaults.SERVICE_MGMT]
    else:
        msg = "Slice setup is currently limited to glusterd.\n"\
              "Ignoring slice setup"
        print(msg)
        Global.logger.info(msg.replace("\n", " "))
    return section_dict, yamls
