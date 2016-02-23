#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#
# Copyright 2015 Nandaja Varma <nvarma@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from gdeploylib import *
from gdeploylib.defaults import *
import os, re


class VolumeManagement(Helpers):

    def __init__(self):
        self.var_file = Global.var_file
        self.get_volume_data()
        self.remove_from_sections('volume')
        self.remove_from_sections('backend-setup.*')

    def get_volume_data(self):
        self.section_lists = self.get_section_dict('volume')
        if not self.section_lists:
            return
        for each in self.section_lists:
            self.section_dict = each
            del self.section_dict['__name__']
            self.volume_action()

    def volume_action(self):
        Global.logger.info("Reading volume section in config")
        action = self.section_dict.get('action')
        volume = self.section_dict.get('volname')
        volname = self.split_volume_and_hostname(volume)
        self.section_dict['volname'] = volname
        smb = self.section_dict.get('smb')
        if not action:
            if smb and smb.lower() == 'yes':
                self.samba_setup()
            else:
                msg = "Section 'volume' without any action option " \
                        "found. \nNoting the data given and skipping this section!"
                print "\nWarning: " + msg
                Global.logger.warning(msg)
            self.filename = Global.group_file
            self.create_var_files(self.section_dict)
            return
        del self.section_dict['action']
        self.section_dict = self.format_values(self.section_dict, 'transport')
        self.filename = Global.group_file
        if not self.is_present_in_yaml(self.filename, 'force'):
            force = self.section_dict.get('force') or ''
            force = 'yes' if force.lower() == 'yes' else 'no'
            self.section_dict['force'] = force
        action_func =  { 'create': self.create_volume,
                          'start': self.start_volume,
                          'delete': self.delete_volume,
                          'stop': self.stop_volume,
                          'add-brick': self.add_brick_to_volume,
                          'remove-brick': self.remove_brick_from_volume,
                          'rebalance': self.gfs_rebalance,
                          'set': self.volume_set
                        }.get(action)
        if not action_func:
            msg = "Unknown action provided for volume. \nSupported " \
                    "actions are:\n " \
                    "create, delete, start, stop, add-brick, remove-brick, " \
                    "rebalance and set"
            print "\nError: " + msg
            Global.logger.error(msg)
            return
        msg = "Volume management(action: %s) triggered" % action
        print "\nINFO: " + msg
        Global.logger.info(msg)
        if not action_func():
            return
        # if not Global.hosts:
            # msg = "Hostnames not provided. Cannot continue!"
            # print "\nError: " + msg
            # Global.logger.error(msg)
            # self.cleanup_and_quit()
        if smb and smb.lower() == 'yes':
            self.samba_setup()

    def get_brick_dirs(self):
        opts = self.get_options('brick_dirs', False)
        return self.pattern_stripping(opts)


    def write_mountpoints(self):
        '''
        host_var files are to be created if multiple hosts
        have different brick_dirs for gluster volume
        '''
        host_files = [self.get_file_dir_path(Global.host_vars_dir,
                    host) for host in Global.hosts]
        files = [Global.group_file] +  host_files
        for fd in files:
            if self.is_present_in_yaml(fd, 'mountpoints'):
                doc = self.read_yaml(fd)
                filename = os.path.basename(fd)
                if filename == 'all':
                    brick_dir = []
                    for h in Global.hosts:
                        brick_dir.extend([h +  ':' +  d for d in
                            doc['mountpoints']])
                else:
                    brick_dir = [filename + ':' +  d for d in
                            doc['mountpoints']]
                self.section_dict['brick_dirs'] = brick_dir
                return
        brick_dirs = []
        if self.get_var_file_type() and Global.var_file == 'group_vars':
            Global.current_hosts = Global.hosts
            brick_dirs = self.get_brick_dirs()
            br_drs = []
            for each in Global.hosts:
                br_drs.extend([each + ':' + brk for brk in brick_dirs])
            self.section_dict['brick_dirs'] = br_drs

        else:
            backend_setup, hosts = self.check_backend_setup_format()
            if backend_setup:
                if not hosts:
                    Global.current_hosts = Global.hosts
                    brick_dirs = self.pattern_stripping(self.config_section_map(
                        'backend-setup', 'brick_dirs', True))
                    for each in Global.hosts:
                        br_drs.extend([each + ':' + brk for brk in brick_dirs])
                    self.section_dict['brick_dirs'] = br_drs
        if  brick_dirs:
            self.filename = Global.group_file
            self.write_brick_dirs(brick_dirs)
        else:
            if hosts:
               Global.current_hosts = hosts
               host_files = [self.get_file_dir_path(Global.host_vars_dir,
                           host) for host in hosts]
               host_sections = ['backend-setup:' + host for host in
                       hosts]
            elif Global.var_file == 'host_vars':
                host_files = [self.get_file_dir_path(Global.host_vars_dir,
                            host) for host in Global.hosts]
                host_sections = Global.hosts
                Global.current_hosts = Global.hosts
            else:
                msg = "Option 'brick_dirs' " \
                        "not found for host .\nCannot continue " \
                        "volume creation!"
                print "\nError:  " + msg
                Global.logger.error(msg)
                self.cleanup_and_quit()
            self.section_dict['brick_dirs'] = []
            for hfile, sec in zip(host_files, host_sections):
                brick_dirs = self.pattern_stripping(Global.sections.get(sec)['brick_dirs'])
                br_drs = [os.path.basename(hfile) + ':' + br for br in
                        brick_dirs]
                self.section_dict['brick_dirs'].extend(br_drs)
                # except:
                    # print "Option 'brick_dirs' " \
                        # "not found.\nCannot continue " \
                        # "volume creation!"
                    # self.cleanup_and_quit()

                self.filename = hfile
                if not self.is_present_in_yaml(self.filename, 'mountpoints'):
                    if not os.path.isfile(self.filename):
                        self.touch_file(self.filename)
                    self.write_brick_dirs(brick_dirs)


    def write_brick_dirs(self, brick_dirs):
       if False in [brick.startswith('/') for brick in brick_dirs]:
           msg = "values to 'brick_dirs' should be absolute"\
                   " path. Relative given. Exiting!"
           print "\nError: " + msg
           Global.logger.error(msg)
           self.cleanup_and_quit()
       self.create_yaml_dict('mountpoints', brick_dirs, False)
       self.create_yaml_dict('brick_dirs', self.section_dict['brick_dirs'], False)


    def create_volume(self):
        if self.section_dict.get('brick_dirs'):
            br_dir = self.pattern_stripping(self.section_dict['brick_dirs'])
            regex = re.compile('(.*):(.*)')
            brick_dir_pat = map(regex.search, br_dir)
            brick_dir_pat = filter(None, brick_dir_pat)
            if not brick_dir_pat:
                if not Global.hosts:
                    print "Please provide the brick_dirs in the format " \
                            "<hostname>:<brick_dir name>"
                    self.cleanup_and_quit()
                else:
                    Global.current_hosts = Global.hosts
                    Global.var_file = Global.group_file
                    self.section_dict['mountpoints'] = br_dir
            else:
                Global.current_hosts = []
                self.section_dict['mountpoints'] = []
                for each in brick_dir_pat:
                    host = each.group(1)
                    if host not in Global.current_hosts:
                        Global.current_hosts.append(host)
                    Global.var_file = self.get_file_dir_path(Global.host_vars_dir, host)
                    self.touch_file(Global.var_file)
                    self.section_dict['mountpoints'].extend(self.pattern_stripping(
                            each.group(2)))
                    self.create_var_files(self.section_dict)
        else:
            if len(self.section_lists) > 1:
                print "\nError: 'brick_dirs' not provided in one or more " \
                "'volume' sections"
                return False
            self.write_mountpoints()
        '''
        This default value dictionary is used to populate the group var
        with default data, if the data is not given by the user/
        '''
        self.set_default_values(self.section_dict, VOLUME_CREATE_DEFAULTS)
        if not self.section_dict['volname']:
            self.section_dict['volname'] = 'glustervol'
        # Custom method for volume config specs
        if self.section_dict['replica'].lower() == 'yes' and int(
                self.section_dict['replica_count']) == 0:
            msg = "Provide the replica count for the volume."
            print "\nError: " + msg
            Global.logger.error(msg)
            self.cleanup_and_quit()
        self.is_option_present('volname', self.section_dict)
        self.run_playbook(GLUSTERD_YML)
        self.create_yaml_dict('hosts', Global.current_hosts, False)
        self.call_peer_probe()
        self.run_playbook(CREATEDIR_YML)
        self.run_playbook(VOLCREATE_YML)
        self.start_volume()
        return True

    def start_volume(self):
        self.is_option_present('volname', self.section_dict)
        Global.current_hosts = Global.hosts
        self.run_playbook(VOLSTART_YML)
        return True

    def stop_volume(self):
        self.is_option_present('volname', self.section_dict)
        Global.current_hosts = Global.hosts
        self.run_playbook(VOLSTOP_YML)
        return True

    def delete_volume(self):
        self.is_option_present('volname', self.section_dict)
        Global.current_hosts = Global.hosts
        self.run_playbook(VOLDEL_YML)
        return True

    def set_default_replica_type(self):
        self.set_default_values(self.section_dict, REPLICA_DEFAULTS)
    def add_brick_to_volume(self):
        self.is_option_present('volname', self.section_dict)
        self.is_option_present('bricks', self.section_dict)
        bricks = self.section_dict.pop('bricks')
        bricks = self.format_brick_names(bricks)
        if not Global.master and not list(
            set(Global.hosts) - set(Global.brick_hosts)):
            msg = "We cannot identify which cluster volume '%s' " \
                    "belongs to.\n\nINFO: We recommend providing " \
                    "'volname' option in the format "\
                    "<hostname>:<volume name>."\
                    "\nElse try giving the name of a different host which "\
                    "is a part of the cluster as value for "\
                    "'hosts' section.\nMake sure it is not the name of the "\
                    "host having the new bricks." \
                    "Exiting!" % self.section_dict.get('volname')
            print "\nError: " + msg
            Global.logger.error(msg)
            self.cleanup_and_quit()

        Global.current_hosts = Global.hosts
        self.section_dict['new_bricks'] = bricks
        self.set_default_replica_type()
        self.is_option_present('volname', self.section_dict)
        self.call_peer_probe()
        self.run_playbook(ADDBRICK_YML)
        return True

    def call_peer_probe(self):
        peer_action = self.config_section_map(
                'peer', 'manage', False) or 'True'
        if peer_action != 'ignore':
            to_be_probed = Global.current_hosts + Global.brick_hosts
            self.create_yaml_dict('to_be_probed', to_be_probed, False)
            self.run_playbook(PROBE_YML)

    def remove_brick_from_volume(self):
        self.is_option_present('volname', self.section_dict)
        self.is_option_present('bricks', self.section_dict)
        if 'state' not in self.section_dict:
            msg = "State of the remove-brick process not " \
                "specified. Can't proceed!\n" \
                "Available options are: {start, stop, force, commit }"
            print "\nError: " + msg
            Global.logger.error(msg)
            self.cleanup_and_quit()
        self.set_default_replica_type()
        self.section_dict['old_bricks'] = self.section_dict.pop('bricks')
        self.is_option_present('volname', self.section_dict)
        Global.current_hosts = Global.hosts
        self.run_playbook(REMOVEBRK_YML)
        return True


    def gfs_rebalance(self):
        if 'state' not in self.section_dict:
            msg = "State of the rebalance process not " \
                "specified. Can't proceed!\n" \
                "Available options are: {start, stop, fix-layout}."
            print "\nError: " + msg
            Global.logger.error(msg)
            self.cleanup_and_quit()
        Global.current_hosts = Global.hosts
        self.run_playbook(VOLUMESTART_YML)
        self.run_playbook(REBALANCE_YML)
        return True

    def volume_set(self, key=None, value=None):
        self.filename = Global.group_file
        if not key:
            self.is_option_present('key', self.section_dict)
            self.is_option_present('value', self.section_dict)
            key = self.section_dict.pop('key')
            value = self.section_dict.pop('value')
        if not isinstance(key, list):
            key = [key]
        if not isinstance(value, list):
            value = [value]
        data = []
        for k,v in zip(key, value):
            names = {}
            names['key'] = k
            names['value'] = v
            data.append(names)
        Global.current_hosts = Global.hosts
        self.create_yaml_dict('set', data, True)
        self.run_playbook(VOLUMESET_YML)
        return True


    def samba_setup(self):
        try:
            ctdb = Global.config._sections['ctdb']
        except:
            msg = "For SMB setup, please ensure you " \
                    "configure 'ctdb' using ctdb " \
                    "section. Refer documentation for more."
            print "Warning: " + msg
            Global.logger.info(msg)
        SMB_DEFAULTS = {
                        'path': '/',
                        'glusterfs:logfile': '/var/log/samba/' +
                            self.section_dict['volname'] + '.log',
                        'glusterfs:loglevel': 7,
                        'glusterfs:volfile_server': 'localhost'
                      }
        self.set_default_values(self.section_dict, SMB_DEFAULTS)
        options = ''
        for key, value in SMB_DEFAULTS.iteritems():
            if self.section_dict[key]:
                options += key + ' = ' + str(self.section_dict[key]) + '\n'
        self.section_dict['smb_options'] = "[gluster-{0}]\n"\
                "comment = For samba share of volume {0}\n"\
                "vfs objects = glusterfs\nglusterfs:volume = {0}\n"\
                "read only = no\nguest ok = "\
                "yes\n{1}".format(self.section_dict['volname'], options)
        Global.current_hosts = Global.hosts

        self.section_dict['smb_username'] = self.section_dict.get('smb_username') or 'smbuser'
        self.section_dict['smb_password'] = self.section_dict.get('smb_password') or 'password'
        if not self.section_dict.get('smb_mountpoint'):
            self.section_dict['smb_mountpoint'] = '/mnt/smbserver'
        self.run_playbook(SMBREPLACE_YML)
        self.run_playbook(SMBSRV_YML)

        key = ['stat-prefetch', 'server.allow-insecure',
                'storage.batch-fsync-delay-usec']
        value = ['off', 'on', 0]
        self.volume_set(key, value)
        self.run_playbook(GLUSTERD_YML)
        return True
