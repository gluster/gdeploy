#!/usr/bin/python
"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Helpers, Global
import os, re

helpers = Helpers()

def openshift_ctl_create(section_dict):
    global helpers
    if not section_dict.get('filename'):
        resource = section_dict.get('resourcename')
        if not resource:
            print "Error: Please provide the resourcename or filename "\
                    "to complete create action"
            helpers.cleanup_and_quit()
        filepath = get_filename(resource, section_dict)
        if not filepath:
            print "Error: Could not find %s file "\
                    "to complete create action" % section_dict.get('filetype')
            helpers.cleanup_and_quit()
    else:
        filepath = section_dict.get('filename')
    section_dict['filepath'] = filepath
    section_dict['filedest'] = os.path.basename(filepath)

    return section_dict, defaults.OC_CREATE

def get_filename(resource, section_dict):
    global helpers
    filenames = []
    filenames.extend(get_templates(Global.extras))
    filenames.extend(get_templates(Global.templates_dir))
    filetype = section_dict.get('filetype')
    if filetype == 'template':
        filepattern = resource + '-template.json'
    elif filetype == 'json':
        filepattern = '.*%s.*.json' % resource
    elif filetype in ['yml', 'yaml']:
        filepattern = '.*%s.*.yml' % resource
    else:
        print "Error: Unknown file type"
        helpers.cleanup_and_quit()

    for each in filenames:
        current = os.path.basename(each)
        if not re.match(filepattern, current):
            continue
        else:
            return each
    return False

def get_templates(dirname):
    filenames = []
    if os.path.exists(dirname):
        files = os.listdir(dirname)
        for each in files:
            filenames.append(helpers.get_file_dir_path(dirname,
                each))
    return filenames
#def kubectl_run(section_dict):
#    return section_dict, defaults.YML_NAME
#
#def kubectl_exec(section_dict):
#    return section_dict, defaults.YML_NAME
#
#def kubectl_get(section_dict):
#    return section_dict, defaults.YML_NAME
#
#def kubectl_delete(section_dict):
#    return section_dict, defaults.YML_NAME
#
#def kubectl_stop(section_dict):
#    return section_dict, defaults.YML_NAME
