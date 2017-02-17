"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Global

def shell_execute(section_dict):
    Global.ignore_errors = section_dict.get('ignore_shell_errors')
    Global.logger.info("Invoking shell command %s"%section_dict['command'])
    return section_dict, defaults.SHELL_YML
