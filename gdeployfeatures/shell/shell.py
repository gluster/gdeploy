#!/usr/bin/python
"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults

def shell_execute(section_dict):
    return section_dict, defaults.SHELL_YML
