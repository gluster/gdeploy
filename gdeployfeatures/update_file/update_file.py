"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults
from gdeploylib import Helpers
from gdeploylib import Global

helpers = Helpers()

def update_file_copy(section_dict):
    global helpers
    src = helpers.listify(section_dict['src'])
    dest = helpers.listify(section_dict['dest'])
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
    if Global.trace:
        Global.logger.info("Executing %s."%defaults.MOVE_FILE)
    return section_dict, defaults.MOVE_FILE

def update_file_edit(section_dict):
    global helpers
    line = helpers.listify(section_dict['line'])
    replace = helpers.listify(section_dict['replace'])
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
    if Global.trace:
        Global.logger.info("Executing %s."%defaults.EDIT_FILE)    
    return section_dict, defaults.EDIT_FILE

def update_file_add(section_dict):
    if Global.trace:
        Global.logger.info("Executing %s."%defaults.ADD_TO_FILE)
    return section_dict, defaults.ADD_TO_FILE

