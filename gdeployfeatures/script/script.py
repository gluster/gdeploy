"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults
from gdeploylib import Helpers, Global

def script_execute(section_dict):
    helpers = Helpers()
    Global.ignore_errors = section_dict.get('ignore_script_errors')
    scriptargs = section_dict['file']
    if type(scriptargs) == list:
        cmd = scriptargs.pop(0)
        # Build rest of the command
        for a in scriptargs:
            cmd += ","+a
    else:
        cmd = scriptargs
    section_dict['script'] = cmd
    return section_dict, defaults.RUN_SCRIPT
