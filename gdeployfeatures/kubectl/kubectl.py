#!/usr/bin/python
"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults

def kubectl_create(section_dict):
    return section_dict, defaults.YML_NAME

def kubectl_run(section_dict):
    return section_dict, defaults.YML_NAME

def kubectl_exec(section_dict):
    return section_dict, defaults.YML_NAME

def kubectl_get(section_dict):
    return section_dict, defaults.YML_NAME

def kubectl_delete(section_dict):
    return section_dict, defaults.YML_NAME

def kubectl_stop(section_dict):
    return section_dict, defaults.YML_NAME
