"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Helpers, Global
import re
from os.path import realpath, basename

helpers = Helpers()

def yum_install(section_dict):
    global helpers
    repo = section_dict.get('repos')
    Global.ignore_errors = section_dict.get('ignore_yum_errors')
    if repo:
        repo = helpers.listify(repo)
        reponame = [re.sub(r'http(s*):\/\/', '', x) for x in repo]
        reponame = [x.rstrip('/').replace('/', '_') for x in reponame]
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
    Global.ignore_errors = section_dict.get('ignore_yum_errors')
    return get_common_data(section_dict)

def get_common_data(section_dict):
    packages = section_dict.pop('packages')
    if type(packages) != list:
        packages = [packages]
    section_dict['name'] = ','.join(packages)
    return section_dict, defaults.YUM_OP
