#!/usr/bin/python
"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Helpers

helpers = Helpers()

def lv_create(section_dict):
    return section_dict, defaults.YML_NAME

def lv_convert(section_dict):
    return section_dict, defaults.YML_NAME

def lv_setup_cache(section_dict):
    global helpers
    section_dict['ssd'] = helpers.correct_brick_format(
            helpers.listify(section_dict['ssd']))
    helpers.perf_spec_data_write()
    return section_dict, defaults.SETUP_CACHE_YML

def lv_change(section_dict):
    return section_dict, defaults.LVCHANGE_YML


