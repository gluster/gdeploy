#!/usr/bin/python
"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Global, Helpers
from collections import defaultdict

helpers = Helpers()

fuse_clients, nfs_clients, cifs_clients = [], [], []
client_mounts = {}
client_mounts = defaultdict(lambda: [], client_mounts)

def clients_mount(section_dict):
    global client_mounts, helpers
    section_dict['volname'] = helpers.split_volume_and_hostname(
            section_dict['volname'])
    clients, mntpts = get_client_hosts(section_dict)
    fstype = helpers.listify(section_dict['fstype'])
    if len(fstype) != len(clients):
        if len(fstype) == 1:
            fstype *= len(mntpts)
        else:
            print "\nError: Provide equal number of fstype and "\
            "clients."
            return False, False
    for mnt, fs, host in zip(mntpts, fstype, clients):
        section_dict = {'glusterfs': fuse_mount,
                        'nfs': nfs_mount,
                        'cifs': cifs_mount
                       }[fs](mnt, host, section_dict)
    if not section_dict:
        return False, False
    write_client_mounts()
    section_dict['clients'] = clients
    helpers.write_to_inventory('clients', clients)
    return section_dict, [defaults.FUSEMNT_YML, defaults.NFSMNT_YML,
            defaults.CIFSMNT_YML]


def nfs_mount(mnt, host, section_dict):
    global client_mounts, helpers
    section_dict['nfsversion'] = section_dict.pop('nfs-version')
    client_mounts[host].append({'mountpoint': mnt, 'fstype': 'nfs'})
    return section_dict


def fuse_mount(mnt, host, section_dict):
    global client_mounts, helpers
    client_mounts[host].append({'mountpoint': mnt, 'fstype': 'fuse'})
    return section_dict

def cifs_mount(mnt, host, section_dict):
    if not section_dict['smb_username'] or not section_dict[
            'smb_password']:
        print "\nError: Provide smb_username and smb_password " \
                "for CIFS mount"
        return False
    global client_mounts, helpers
    client_mounts[host].append({'mountpoint': mnt, 'fstype': 'cifs'})
    return section_dict

def write_client_mounts():
    global client_mounts, helpers
    for host, value in client_mounts.iteritems():
        filename = helpers.get_file_dir_path(Global.host_vars_dir, host)
        helpers.touch_file(filename)
        helpers.create_yaml_dict('client_mounts', value, filename)
    return

def clients_unmount(section_dict):
    global helpers
    clients, mntpts = get_client_hosts(section_dict)
    for mnt, host in zip(mntpts, clients):
        filename = helpers.get_file_dir_path(Global.host_vars_dir, host)
        helpers.touch_file(filename)
        helpers.create_yaml_dict('mountpoint', mnt, filename)
    section_dict['clients'] = clients
    helpers.write_to_inventory('clients', clients)
    del section_dict['hosts']
    return section_dict, defaults.VOLUMOUNT_YML


def get_client_hosts(section_dict):
    global helpers
    clients = helpers.listify(section_dict['hosts'])
    try:
        mntpts = helpers.listify(section_dict['client_mount_points'])
    except:
        mntpts = ['/mnt/client' +
                str(i) for i in range(len(clients) + 1)]
    if len(clients) != len(mntpts):
        if len(mntpts) == 1:
            mntpts *= len(clients)
        elif len(clients) == 1:
            clients *= len(mntpts)
        else:
            print "\nError: Provide equal number of client hosts and "\
            "client_mount_points."
            self.cleanup_and_quit()
    return clients, mntpts
