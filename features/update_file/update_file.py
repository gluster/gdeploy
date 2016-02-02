#!/usr/bin/python
"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from lib import defaults

def update_file_copy(section_dict):
    src = listify(section_dict['src'])
    dest = listify(section_dict['dest'])
    if len(dest) == 1:
        dest *= len(src)
    if len(dest) != len(src):
        print "\nError: Provide same number of 'src' and 'dest' or " \
                "provide a common 'dest'"
        return None, None
    data = []
    for sr, de in zip(src, dest):
        files_list = {}
        files_list['src'] = sr
        files_list['dest'] = de
        data.append(files_list)
    section_dict['file_paths'] = data
    return section_dict, defaults.MOVE_FILE

def update_file_edit(section_dict):
    line = listify(section_dict['line'])
    replace = listify(section_dict['replace'])
    data = []
    if len(replace) != len(line):
        print "\nError: Provide same number of 'replace' and 'line'"
        return
    for li, re in zip(line, replace):
        files_list = {}
        files_list['line'] = li
        files_list['replace'] = re
        data.append(files_list)
    section_dict['file_paths'] = data
    return section_dict, defaults.EDIT_FILE

def update_file_add(section_dict):
    return section_dict, defaults.ADD_TO_FILE

def listify(var):
    if not type(var) is list:
        return [var]
    return var
