"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Global

def peer_probe(section_dict):
    if not check_for_host_names():
        return False, False
    Global.ignore_errors = section_dict.get('ignore_peer_errors')
    to_be_probed = Global.hosts + Global.brick_hosts
    to_be_probed = sorted(set(to_be_probed))
    section_dict['to_be_probed'] = to_be_probed
    return section_dict, defaults.PROBE_YML

def peer_detach(section_dict):
    Global.ignore_errors = section_dict.get('ignore_peer_errors')
    section_dict['hosts'] = Global.hosts
    if not check_for_host_names():
        return False, False
    return section_dict, defaults.DETACH_YML

def peer_ignore(section_dict):
    return section_dict, ''

def check_for_host_names():
    if not Global.hosts:
        msg = "Although peer manage option is provided, " \
                "no hosts are provided in the section. \n " \
                "Skipping section `peer`"
        print "\nError: " + msg
        Global.logger.error(msg)
        return False
    return True
