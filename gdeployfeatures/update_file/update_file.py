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
    Global.ignore_errors = section_dict.get('ignore_update_file_errors')
    if len(dest) == 1:
        dest *= len(src)
    if len(dest) != len(src):
        msg = "Provide same number of 'src' and 'dest' or " \
              "provide a common 'dest'"
        print "Error: %s"%msg
        Global.logger.error(msg)
        return None, None
    data = []
    for sr, de in zip(src, dest):
        files_list = {}
        files_list['src'] = sr
        files_list['dest'] = de
        data.append(files_list)
    section_dict['file_paths'] = data
    Global.logger.info("Updating files %s by copying"%data)
    return section_dict, defaults.MOVE_FILE

def update_file_edit(section_dict):
    global helpers
    line = helpers.listify(section_dict['line'])
    replace = helpers.listify(section_dict['replace'])
    data = []
    Global.ignore_errors = section_dict.get('ignore_update_file_errors')
    if len(replace) != len(line):
        msg = "Provide same number of 'replace' and 'line'"
        print "Error: %s"%msg
        Global.logger.error(msg)
        return
    for li, re in zip(line, replace):
        files_list = {}
        files_list['line'] = li
        files_list['replace'] = re
        data.append(files_list)
    section_dict['file_paths'] = data
    Global.logger.info("Editing file %s with %s"%(section_dict['dest'], data))
    return section_dict, defaults.EDIT_FILE

def update_file_add(section_dict):
    Global.ignore_errors = section_dict.get('ignore_update_file_errors')
    Global.logger.info("Adding lines to file")
    return section_dict, defaults.ADD_TO_FILE

def update_file_delete_line(section_dict):
    global helpers
    line = helpers.listify(section_dict['line'])
    data = []
    Global.ignore_errors = section_dict.get('ignore_update_file_errors')
    for li in line:
        files_list = {}
        files_list['line'] = li
        data.append(files_list)
    section_dict['file_paths'] = data
    Global.logger.info("Deleting line %s in file %s"%(data, section_dict['dest']))
    return section_dict, defaults.DELETE_LINE_FILE
