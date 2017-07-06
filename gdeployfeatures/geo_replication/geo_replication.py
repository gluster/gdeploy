"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults
from gdeploylib import Helpers, Global

helpers = Helpers()

def geo_replication_create(section_dict):
    section_dict = parse_georep_data(section_dict)
    section_dict['base_dir'] = Global.base_dir
    populate_inventory(section_dict)
    Global.logger.info("Initiating georep create")
    georep_setup = [ defaults.GEOREP_SETUP_MASTER,
                     defaults.GEOREP_SETUP_SLAVE_USERGRP,
                     defaults.GEOREP_SETUP_MOUNTBROKER,
                     defaults.GEOREP_SETUP_GLUSTERD_RESTART,
                     defaults.GEOREP_SETUP_SLAVE_PEM,
                     defaults.GEOREP_SETUP_SESSION_CREATE ]
    if section_dict['start'] == 'yes':
        georep_setup += [ defaults.GEOREP_START ]
    return section_dict, georep_setup

def geo_replication_start(section_dict):
    section_dict = parse_georep_data(section_dict)
    populate_inventory(section_dict)
    Global.logger.info("Starting georeplication")
    return section_dict, defaults.GEOREP_START

def geo_replication_stop(section_dict):
    section_dict = parse_georep_data(section_dict)
    populate_inventory(section_dict)
    Global.logger.info("Stopping georep session")
    return section_dict, defaults.GEOREP_STOP

def geo_replication_pause(section_dict):
    section_dict = parse_georep_data(section_dict)
    populate_inventory(section_dict)
    Global.logger.info("Pausing georep session")
    return section_dict, defaults.GEOREP_PAUSE

def geo_replication_delete(section_dict):
    section_dict = parse_georep_data(section_dict)
    populate_inventory(section_dict)
    Global.logger.info("Deleting georep session")
    return section_dict, [defaults.GEOREP_STOP, defaults.GEOREP_DELETE]

def geo_replication_resume(section_dict):
    section_dict = parse_georep_data(section_dict)
    populate_inventory(section_dict)
    Global.logger.info("Resuming georep session")
    return section_dict, defaults.GEOREP_RESUME

def geo_replication_config(section_dict):
    section_dict = parse_georep_data(section_dict)
    populate_inventory(section_dict)
    Global.logger.info("Configuring georep setup")
    return section_dict, defaults.GEOREP_CONFIG

def geo_replication_failover(section_dict):
    section_dict = parse_georep_data(section_dict)
    (section_dict['master'], section_dict['slave']) = (section_dict['slave'],
                                                       section_dict['master'])
    (section_dict['mastervolname'], section_dict['slavevolname']) = (
        section_dict['slavevolname'], section_dict['mastervolname'])
    populate_inventory(section_dict)
    section_dict['volname'] = section_dict['slavevolname']
    section_dict['key'] = ['geo-replication.indexing', 'changelog']
    section_dict['value'] = 'on'
    section_dict['config'] = 'special-sync-mode'
    section_dict['op'] = 'recover'
    section_dict['checkpoint'] = 'now'
    Global.master = section_dict['slave']
    Global.logger.info("Configuring georep failover")
    return section_dict, [defaults.VOLUMESET_YML,
                          defaults.GEOREP_CREATE, defaults.GEOREP_CONFIG,
                          defaults.GEOREP_START]

def geo_replication_failback(section_dict):
    section_dict = parse_georep_data(section_dict)
    populate_inventory(section_dict)
    section_dict['checkpoint'] = 'now'
    section_dict['volname'] = section_dict['slavevolname']
    section_dict['key'] = ['geo-replication.indexing', 'changelog']
    Global.master = section_dict['slave']
    Global.logger.info("Configuring georep failback")
    return section_dict, [defaults.GEOREP_CONFIG, defaults.GEOREP_FAILBACK]

def parse_georep_data(section_dict):
    global helpers
    section_dict['mastervolname'] = helpers.split_volume_and_hostname(
        section_dict['mastervol'])
    section_dict['master'] = Global.master
    section_dict['slavevolname'] = helpers.split_volume_and_hostname(
        section_dict['slavevol'])
    section_dict['slave'] = Global.master
    return section_dict

def populate_inventory(section_dict):
    global helpers
    helpers.write_to_inventory('georep_master', [section_dict['master'][0]])
    helpers.write_to_inventory('georep_slave', [section_dict['slave'][0]])
    try:
        helpers.write_to_inventory('georep_slaves', section_dict['slavenodes'])
    except KeyError:
        pass
