#!/usr/bin/python
"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Helpers
helpers = Helpers()

def rh_subscription_register(section_dict):
    return register_and_subscribe(section_dict)

def rh_subscription_unregister(section_dict):
    return section_dict, defaults.UNREGISTER

def rh_subscription_enable_repos(section_dict):
    section_dict, ret = register_and_subscribe(section_dict)
    return section_dict, defaults.ENABLE_REPO

def rh_subscription_disable_repos(section_dict):
    global helpers
    repos = section_dict.get('repos')
    section_dict['repos'] = helpers.listify(repos) if repos else "\'*\'"
    return section_dict, defaults.DISABLE_REPO

def rh_subscription_attach_pool(section_dict):
    return register_and_subscribe(section_dict)

def register_and_subscribe(section_dict):
    global helpers
    repos = section_dict.get('repos')
    section_dict['rhsm_repos'] = helpers.listify(repos) if repos else []
    section_dict['attach'] = section_dict.get('auto-attach') or 'false'
    return section_dict, defaults.SUBS_MGMT
