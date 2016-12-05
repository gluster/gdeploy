"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults
from gdeploylib import Helpers, Global

def script_execute(section_dict):
    helpers = Helpers()
    section_dict['file'] = helpers.listify(section_dict['file'])
    files_l = len(section_dict['file'])
    if not section_dict.get('args'):
        section_dict['args'] = [''] * files_l
    section_dict['args'] = helpers.listify(section_dict['args'])
    args_l = len(section_dict['args'])

    length_match = False
    if args_l != files_l:
        if files_l > args_l:
            if args_l == 1:
                length_match = True
                section_dict['args'] *= files_l
    else:
        length_match = True
    if not length_match:
        msg = "Mismatch in the number of arguments " \
              "and the number of shell scripts."
        print "Error: %s"%msg
        Global.logger.error(msg)
        return section_dict, None
    data = []
    for sh, args in zip(section_dict['file'], section_dict['args']):
        data.append(sh + ' ' + args)
    section_dict['script'] = data
    Global.logger.info("Executing script %s"%section_dict['file'])
    return section_dict, defaults.RUN_SCRIPT
