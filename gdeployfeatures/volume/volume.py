"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Helpers, Global, YamlWriter
import os, re
from os.path import basename
from collections import defaultdict

helpers = Helpers()
writers = YamlWriter()

def volume_create(section_dict):
    global helpers
    Global.ignore_errors = section_dict.get('ignore_volume_errors')
    section_dict['volname'] = helpers.split_volume_and_hostname(
            section_dict['volname'])
    if not section_dict.get('brick_dirs'):
       section_dict = get_common_brick_dirs(section_dict)
    else:
        section_dict = validate_brick_dirs(section_dict, 'brick_dirs')
    Global.logger.info("Creating volume %s with bricks %s"%
                       (section_dict['volname'], section_dict['brick_dirs']))
    section_dict['service'] = 'glusterd'
    section_dict['state'] = 'started'
    Global.current_hosts = helpers.unique(Global.current_hosts)
    section_dict['hosts'] = Global.current_hosts
    yamls = [defaults.SERVICE_MGMT, defaults.CREATEDIR_YML]
    Global.logger.info("Calling peer probe from volume create")
    ret = call_peer_probe(section_dict)
    if ret:
        section_dict = ret
        yamls.append(defaults.PROBE_YML)
    yamls.append(defaults.VOLCREATE_YML)
    Global.logger.info("Setting volume options (if any)")
    section_dict, set_yml = volume_set(section_dict)
    if set_yml:
        yamls.append(set_yml)
    Global.logger.info("Starting volume %s"%section_dict['volname'])
    section_dict, start_yml = volume_start(section_dict)
    yamls.append(start_yml)
    sdict, yml = get_smb_data(section_dict)
    if sdict:
        yml = helpers.listify(yml)
        section_dict = sdict
        yamls.extend(yml)
    if type(section_dict['transport']) is list:
        section_dict['transport'] = ','.join(section_dict['transport'])
    # Configure SSL on the volume if enable_ssl is set.
    if section_dict['enable_ssl'].lower() == "yes":
        if section_dict.has_key('ssl_clients'):
            section_dict['ssl_hosts'] = list(set(helpers.listify
                                                 (section_dict['ssl_clients'])\
                                                  + Global.hosts))
        else:
            section_dict['ssl_hosts'] = list(set(Global.hosts))

        section_dict['ssl_allow_list'] = ','.join(section_dict['ssl_hosts'])
        section_dict['ssl_base_dir'] = Global.base_dir
        helpers.write_to_inventory('ssl_hosts', section_dict['ssl_hosts'])
        # Enable SSL on the volume
        Global.logger.info("Enabling ssl on the volume")
        yamls += [defaults.SSL_GEN_KEYS, defaults.SSL_VOL_SET,
                  defaults.SSL_RESTART_SERVICES,
                  defaults.SSL_VOL_START]
    return section_dict, yamls

def get_smb_data(section_dict):
    smb = section_dict.get('smb')
    if smb:
        if smb.lower() == 'yes':
            return volume_smb_setup(section_dict)
        elif smb.lower() == 'no':
            return volume_smb_disable(section_dict)
    return False, False

def call_peer_probe(section_dict):
    global helpers
    peer_action = helpers.config_section_map(
            'peer', 'action', False) or 'True'
    if peer_action != 'ignore':
        to_be_probed = Global.current_hosts + Global.brick_hosts
        to_be_probed = helpers.unique(to_be_probed)
        section_dict['to_be_probed'] = to_be_probed
        return section_dict
    Global.logger.info("Probing peers %s"%section_dict['to_be_probed'])
    return False

def get_common_brick_dirs(section_dict):
    global helpers, writers
    f_brick_list, brick_name  = [], []
    host_files = os.listdir(Global.host_vars_dir)
    for host in host_files:
        filename = helpers.get_file_dir_path(Global.host_vars_dir,
                host)
        ret = read_brick_dir_from_file(filename)
        if not ret:
            continue
        brick_list, brick_name = ret
        check_brick_name_format(brick_name)
        writers.create_yaml_dict('brick_dirs', sorted(
            set(brick_name)), filename)
        Global.brick_hosts.append(host)
        f_brick_list.extend(brick_list)


    if set(Global.current_hosts) - set(Global.brick_hosts):
        ret = read_brick_dir_from_file(Global.group_file)
        if ret:
            brick_list, brick_name = ret
            check_brick_name_format(brick_name)
            f_brick_list.extend(brick_list)
            section_dict['brick_dirs'] = helpers.unique(brick_name)
        else:
            msg = "Error: 'brick_dirs' not provided for all the "\
                  "hosts."
            print msg
            Global.logger.error(msg)
            helpers.cleanup_and_quit()

    section_dict['mountpoints'] = helpers.unique(f_brick_list)
    return section_dict

def read_brick_dir_from_file(filename):
    global helpers, writers
    brick_list, brick_name = [], []
    if basename(filename) == 'all':
        hostlist = Global.current_hosts
    else:
        hostlist = [basename(filename)]
    if helpers.is_present_in_yaml(filename, 'mountpoints'):
        brick_name = helpers.get_value_from_yaml(filename,
                'mountpoints')
        for each in brick_name:
            brick_list.extend([host + ':' + each for host in
                hostlist])
        return (brick_list, brick_name)
    return False

def validate_brick_dirs(section_dict, section):
    global helpers, writers
    brick_list, brick_name = [], []
    brick_dict = {}
    brick_dict = defaultdict(lambda: [], brick_dict)
    brick_dirs = helpers.listify(section_dict[section])
    for brick in brick_dirs:
        bpat = re.match('(.*):(.*)', brick)
        if not bpat:
            if not Global.hosts:
                msg = "Please provide the brick_dirs in the format " \
                      "<hostname>:<brick_dir name>"
                print "Error: %s"%msg
                Global.logger.error(msg)
                helpers.cleanup_and_quit()
            brick_list.extend([host + ':' + brick for host in
                Global.hosts])
            brick_name.append(brick)
        else:
            brick_list.append(brick)
            brick_name.append(bpat.group(2))
            brick_dict[bpat.group(1)].append(bpat.group(2))
            if bpat.group(1) not in Global.brick_hosts:
                Global.brick_hosts.append(bpat.group(1))
    if brick_dict:
        for host, bname in zip(brick_dict.keys(), brick_dict.values()):
            filename = helpers.get_file_dir_path(Global.host_vars_dir, host)
            helpers.touch_file(filename)
            helpers.create_yaml_dict('brick_dirs', bname, filename)

    check_brick_name_format(brick_name)
    section_dict['brick_dirs']  = helpers.unique(brick_name)
    section_dict['mountpoints'] = helpers.unique(brick_list)
    return section_dict

def check_brick_name_format(brick_name):
    global helpers
    if False in [brick.startswith('/') for brick in
           helpers.unique(brick_name)]:
        msg = "Values to 'brick_dirs' should be absolute"\
               " path. Relative given. Exiting!"
        print "Error: %s"%msg
        Global.logger.error(msg)
        helpers.cleanup_and_quit()
    return

def volume_delete(section_dict):
    global helpers
    Global.ignore_errors = section_dict.get('ignore_volume_errors')
    section_dict['volname'] = helpers.split_volume_and_hostname(
            section_dict['volname'])
    return section_dict, defaults.VOLDEL_YML

def volume_start(section_dict):
    global helpers
    Global.ignore_errors = section_dict.get('ignore_volume_errors')
    section_dict['volname'] = helpers.split_volume_and_hostname(
            section_dict['volname'])
    return section_dict, defaults.VOLUMESTART_YML

def volume_stop(section_dict):
    global helpers
    Global.ignore_errors = section_dict.get('ignore_volume_errors')
    section_dict['volname'] = helpers.split_volume_and_hostname(
            section_dict['volname'])
    Global.logger.info("Stopping volume %s"%section_dict['volname'])
    return section_dict, defaults.VOLSTOP_YML

def volume_add_brick(section_dict):
    global helpers
    Global.ignore_errors = section_dict.get('ignore_volume_errors')
    yamls = []
    section_dict['volname'] = helpers.split_volume_and_hostname(
            section_dict['volname'])
    section_dict = validate_brick_dirs(section_dict, 'bricks')
    ret = call_peer_probe(section_dict)
    if ret:
        section_dict = ret
        yamls.append(defaults.PROBE_YML)
    Global.logger.info("Adding bricks %s to volume %s"%
                       (section_dict['bricks'], section_dict['volname']))
    yamls.append(defaults.ADDBRICK_YML)
    return section_dict, yamls

def volume_remove_brick(section_dict):
    global helpers
    Global.ignore_errors = section_dict.get('ignore_volume_errors')
    section_dict['volname'] = helpers.split_volume_and_hostname(
            section_dict['volname'])
    section_dict['old_bricks'] = section_dict.pop('bricks')
    Global.logger.info("Removing bricks %s from volume %s"%
                       (section_dict['old_bricks'], section_dict['volname']))
    return section_dict, defaults.REMOVEBRK_YML

def volume_rebalance(section_dict):
    global helpers
    Global.ignore_errors = section_dict.get('ignore_volume_errors')
    section_dict['volname'] = helpers.split_volume_and_hostname(
            section_dict['volname'])
    return section_dict, [defaults.VOLUMESTART_YML,
                          defaults.REBALANCE_YML]

def volume_set(section_dict):
    global helpers
    Global.ignore_errors = section_dict.get('ignore_volume_errors')
    section_dict['volname'] = helpers.split_volume_and_hostname(
            section_dict['volname'])
    keys = section_dict.get('key')
    values = section_dict.get('value')
    if not keys or not values:
        return section_dict, ''

    data = []
    key = helpers.listify(keys)
    value = helpers.listify(values)

    # If values has a string and is semicolon separated, replace with
    # comma
    for idx, item in enumerate(value):
        if type(item) == str and item.__contains__(';'):
            value[idx] = item.replace(';', ',')

    for k,v in zip(key, value):
        names = {}
        names['key'] = k
        names['value'] = v
        data.append(names)
    section_dict['set'] = data
    return section_dict, defaults.VOLUMESET_YML

def volume_smb_setup(section_dict):
    global helpers
    Global.ignore_errors = section_dict.get('ignore_volume_errors')
    section_dict['volname'] = helpers.split_volume_and_hostname(
            section_dict['volname'])
    SMB_DEFAULTS = {
                    'glusterfs:logfile': '/var/log/samba/' +
                        section_dict['volname'] + '.log',
                   }
    section_dict = helpers.set_default_values(section_dict, SMB_DEFAULTS)
    options = ''
    for key, value in SMB_DEFAULTS.iteritems():
        if section_dict[key]:
            options += key + ' = ' + str(section_dict[key]) + '\n'
    section_dict['key'] = ['server.allow-insecure',
                           'storage.batch-fsync-delay-usec', 'group',
                           'user.cifs']
    section_dict['value'] = ['on', 0, 'samba', 'enable']
    section_dict, yml = volume_set(section_dict)
    section_dict['service'] = 'glusterd'
    section_dict['state'] = 'started'
    Global.logger.info("Setting up Samba on volume %s"%
                       section_dict['volname'])
    return section_dict, [defaults.SERVICE_MGMT, yml, defaults.SMBREPLACE_YML,
                          defaults.SMBSRV_YML]

def volume_smb_disable(section_dict):
    section_dict['key'] = "user.smb"
    section_dict['value'] = "disable"
    return volume_set(section_dict)

def volume_enable_ssl(section_dict):
    """
    Enable ssl on an existing volume
    """
    print "Ensure clients are unmounted before continuing. Add umount "\
    "section in config."
    if section_dict.has_key('ssl_clients'):
        section_dict['ssl_hosts'] = list(set(section_dict['ssl_clients'] +
                                             Global.hosts))
    else:
        section_dict['ssl_hosts'] = list(set(Global.hosts))

    section_dict['ssl_allow_list'] = ','.join(section_dict['ssl_hosts'])
    section_dict['ssl_base_dir'] = Global.base_dir
    helpers.write_to_inventory('ssl_hosts', section_dict['ssl_hosts'])
    # Enable SSL on the volume
    return section_dict, [defaults.SSL_GEN_KEYS, defaults.SSL_VOL_SET,
                          defaults.SSL_RESTART_SERVICES,
                          defaults.SSL_VOL_START]

def volume_replace_brick(section_dict):
    """Replace a brick in GlusterFS volume."""
    Global.logger.info("Replacing bricks %s"%section_dict['bricks'])
    Global.ignore_errors = section_dict.get('ignore_volume_errors')
    return section_dict, defaults.REPLACE_BRICK
