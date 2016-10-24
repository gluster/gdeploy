"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Helpers, Global
helpers = Helpers()

def rh_subscription_register(section_dict):
    Global.ignore_errors = section_dict.get('ignore_register_errors')
    return register_and_subscribe(section_dict)

def rh_subscription_unregister(section_dict):
    Global.ignore_errors = section_dict.get('ignore_unregister_errors')
    if Global.trace:
        Global.logging.info("Executing %s."%defaults.UNREGISTER)
    return section_dict, defaults.UNREGISTER

def rh_subscription_enable_repos(section_dict):
    Global.ignore_errors = section_dict.get('ignore_enable_errors')
    section_dict, ret = register_and_subscribe(section_dict)
    if Global.trace:
        Global.logging.info("Executing %s."%defaults.ENABLE_REPO)
    return section_dict, defaults.ENABLE_REPO

def rh_subscription_disable_repos(section_dict):
    global helpers
    repos = section_dict.get('repos')
    Global.ignore_errors = section_dict.get('ignore_disable_errors')
    section_dict['repos'] = helpers.listify(repos) if repos else "\'*\'"
    if Global.trace:
        Global.logging.info("Executing %s."%defaults.DISABLE_REPO)
    return section_dict, defaults.DISABLE_REPO

def rh_subscription_attach_pool(section_dict):
    Global.ignore_errors = section_dict.get('ignore_attach_pool_errors')
    return register_and_subscribe(section_dict)

def register_and_subscribe(section_dict):
    global helpers
    repos = section_dict.get('repos')
    section_dict['rhsm_repos'] = helpers.listify(repos) if repos else []
    section_dict['attach'] = section_dict.get('auto-attach') or 'false'
    if Global.trace:
        Global.logging.info("Executing %s."%defaults.SUBS_MGMT)
    return section_dict, defaults.SUBS_MGMT
