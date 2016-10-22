"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Helpers, Global
import os, re

helpers = Helpers()

def openshift_ctl_create(section_dict):
    global helpers
    filepaths = helpers.listify(section_dict.get('filename'))
    if not filepaths:
        resource = helpers.listify(section_dict.get('resourcename'))
        if not resource:
            print "Error: Please provide the resourcename or filename "\
                    "to complete create action"
            helpers.cleanup_and_quit()
        filepaths = get_filename(resource, section_dict)
    data = []
    for filepath in filepaths:
        filelist = {}
        var = section_dict.get('variable')
        if not var:
            var = section_dict.get('variable' + str(filepaths.index(filepath) +1))
        var = ','.join(helpers.listify(var)) if var else ''
        filelist['filepath'] = filepath
        filelist['filedest'] = os.path.basename(filepath)
        filelist['variable'] = var
        data.append(filelist)
    section_dict['filelist'] = data
    return section_dict, defaults.OC_CREATE

def get_filename(resources, section_dict):
    global helpers
    filenames = []
    filenames.extend(get_templates(Global.extras))
    filenames.extend(get_templates(Global.templates_dir))
    filetype = section_dict.get('filetype')
    filelist = []
    for resource in resources:
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
                filename = ''
                continue
            else:
                filename = each
                break
        if not filename:
            print "Error: Could not find %s file for %s"\
                    " to complete create action" % (
                            section_dict.get('filetype'), resource)
            helpers.cleanup_and_quit()
        filelist.append(filename)

    return filelist

def get_templates(dirname):
    filenames = []
    if os.path.exists(dirname):
        files = os.listdir(dirname)
        for each in files:
            filenames.append(helpers.get_file_dir_path(dirname,
                each))
    return filenames



def openshift_ctl_delete(section_dict):
    global helpers
    typename = ','.join(helpers.listify(section_dict.get('type')))
    section_dict['type'] = typename
    section_dict['filename'] = get_unique_item_names(section_dict,
            'filename') or None
    section_dict['resourcename'] =  get_unique_item_names(section_dict,
            'resourcename') or None
    section_dict['label'] = get_unique_item_names(section_dict, 'label') or None
    section_dict['uuid'] = get_unique_item_names(section_dict, 'uuid') or None
    return section_dict, defaults.OC_DELETE

def get_unique_item_names(section_dict, option):
    global helpers
    name = helpers.listify(section_dict.get(option))
    if not name:
        return None
    uniqueval = filter(None, map(lambda s: s.strip(), name))
    return uniqueval

#def kubectl_run(section_dict):
#    return section_dict, defaults.YML_NAME
#
#def kubectl_exec(section_dict):
#    return section_dict, defaults.YML_NAME
#
#def kubectl_get(section_dict):
#    return section_dict, defaults.YML_NAME
#
#
#def kubectl_stop(section_dict):
#    return section_dict, defaults.YML_NAME
