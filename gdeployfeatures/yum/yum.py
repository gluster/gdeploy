#!/usr/bin/python
"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Helpers
import os

helpers = Helpers()

def yum_install(section_dict):
    global helpers
    repo = section_dict.get('repos')
    if repo:
        repo = helpers.listify(repo)
        repo = [x.strip('/') for x in repo]
        reponame = [os.path.basename(x) for x in repo]
        data = []
        for url, name in zip(repo, reponame):
            repolist = dict()
            repolist['name'] = name
            repolist['url'] = url
            data.append(repolist)
        section_dict['repolist'] = data
    section_dict['yum_state'] = 'present'
    return get_common_data(section_dict)

def yum_remove(section_dict):
    section_dict['yum_state'] = 'absent'
    return get_common_data(section_dict)

def get_common_data(section_dict):
    section_dict['name'] = section_dict.pop('packages')
    return section_dict, defaults.YUM_OP
