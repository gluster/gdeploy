"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults
from gdeploylib import Global

def shell_execute(section_dict):
	if Global.trace:
		Global.logging.info("Executing %s."%defaults.SHELL_YML)
    return section_dict, defaults.SHELL_YML
