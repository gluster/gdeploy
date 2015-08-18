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

from yaml_writer import YamlWriter
from conf_parser import ConfigParseHelpers
from global_vars import Global
from helpers import Helpers


class VolumeManagement(YamlWriter):

    def __init__(self, config, filetype):
        self.config = config
        self.filetype = filetype
        try:
            self.section_dict = self.config._sections['volume']
            del self.section_dict['__name__']
        except KeyError:
            return
        action = self.section_dict.get('action')
        volume = self.section_dict.get('volname')
        volname = self.split_volname_and_hostname(volume)
        self.section_dict['volname'] = volname
        if not action:
            self.filename = Global.group_file
            self.iterate_dicts_and_yaml_write(self.section_dict)
            return
        self.fix_format_of_values_in_config(self.section_dict, 'transport')
        action_func =  { 'create': self.create_volume,
                          'start': self.start_volume,
                          'delete': self.delete_volume,
                          'stop': self.stop_volume,
                          'add-brick': self.add_brick_to_volume,
                          'remove-brick': self.remove_brick_from_volume,
                          'rebalance': self.gfs_rebalance
                        }.get(action)
        if not action_func:
            print "\nError: Unknown action provided for volume. \nSupported " \
                    "actions are:\n " \
                    "create, delete, start, stop, add-brick, remove-brick, " \
                    "and rebalance"
            return
        action_func()
        volname = self.split_volname_and_hostname(self.section_dict['volname'])
        self.section_dict['volname'] = volname
        if not Global.hosts:
            print "Error: Hostnames not provided. Cannot continue!"
            self.cleanup_and_quit()
        self.filename = Global.group_file
        print "INFO: Volume management(action: %s) triggered" % action
        if self.section_dict.get('force') == 'yes':
            print "\nWarning: Using mountpoint itself as the brick in one or " \
                    "more hosts since force" \
                " is specified, although not recommended.\n"
        self.iterate_dicts_and_yaml_write(self.section_dict)

    def write_brick_dirs(self):
        '''
        host_var files are to be created if multiple hosts
        have different brick_dirs for gluster volume
        '''
        if self.filetype == 'group_vars':
            if not self.present_in_yaml(Global.group_file, 'mountpoints'):
                self.filename = Global.group_file
                brick_dirs = self.get_options('brick_dirs', False)
                if not brick_dirs:
                    print "Error: Section 'brick_dirs' or 'mountpoints' " \
                            "not found.\nCannot continue volume creation!"
                    self.cleanup_and_quit()
                self.create_yaml_dict('mountpoints', brick_dirs, False)
        else:
            for host in Global.hosts:
                self.filename = self.get_file_dir_path(Global.host_vars_dir, host)
                if not self.present_in_yaml(self.filename, 'mountpoints'):
                    self.touch_file(self.filename)
                    brick_dirs = self.get_options('brick_dirs', False)
                    if not brick_dirs:
                        print "Error: Option 'brick_dirs' or 'mountpoints' " \
                                "not found for host %s.\nCannot continue " \
                                "volume creation!" % host
                        self.cleanup_and_quit()
                    self.create_yaml_dict('mountpoints', brick_dirs, False)

    def create_volume(self):
        self.write_brick_dirs()
        '''
        This default value dictionary is used to populate the group var
        with default data, if the data is not given by the user/
        '''
        sections_default_value = {
            'volname': 'glustervol',
            'transport': 'tcp',
            'replica': 'no',
            'disperse': 'no',
            'replica_count': 0,
            'arbiter_count': 0,
            'disperse_count': 0,
            'redundancy_count': 0}
        self.set_default_value_for_dict_key(self.section_dict,
                                            sections_default_value)
        # Custom method for volume config specs
        if self.section_dict['replica'].lower() == 'yes' and int(
                self.section_dict['replica_count']) == 0:
            print "Error: Provide the replica count for the volume."
            self.cleanup_and_quit()
        self.check_for_param_presence('volname', self.section_dict)
        if 'gluster-peer-probe.yml' not in Global.playbooks:
            Global.playbooks.append('glusterd-start.yml')
            Global.playbooks.append('gluster-peer-probe.yml')
        Global.playbooks.append('create-brick-dirs.yml')
        Global.playbooks.append('gluster-volume-create.yml')
        self.start_volume()

    def start_volume(self):
        self.check_for_param_presence('volname', self.section_dict)
        Global.playbooks.append('gluster-volume-start.yml')

    def stop_volume(self):
        self.check_for_param_presence('volname', self.section_dict)
        Global.playbooks.append('gluster-volume-stop.yml')

    def delete_volume(self):
        self.check_for_param_presence('volname', self.section_dict)
        Global.playbooks.append('gluster-volume-delete.yml')

    def set_default_replica_type(self):
        sections_default_value = {
            'replica': 'no',
            'replica_count': 0}
        self.set_default_value_for_dict_key(self.section_dict,
                                            sections_default_value)
    def add_brick_to_volume(self):
        self.check_for_param_presence('bricks', self.section_dict)
        self.section_dict['new_bricks'] = self.section_dict.pop('bricks')
        if isinstance(self.section_dict['new_bricks'], list):
            for brick in self.section_dict['new_bricks']:
                self.split_volname_and_hostname(brick)
        else:
            self.split_volname_and_hostname(self.section_dict['new_bricks'])
        self.set_default_replica_type()
        self.check_for_param_presence('volname', self.section_dict)
        if 'gluster-peer-probe.yml' not in Global.playbooks:
            Global.playbooks.append('gluster-peer-probe.yml')
        Global.playbooks.append('gluster-add-brick.yml')

    def remove_brick_from_volume(self):
        self.check_for_param_presence('bricks', self.section_dict)
        if 'state' not in self.section_dict:
            print "Error: State of the remove-brick process not " \
                "specified. Can't proceed!\n" \
                "Available options are: {start, stop, force, commit }"
            self.cleanup_and_quit()
        self.set_default_replica_type()
        self.section_dict['old_bricks'] = self.section_dict.pop('bricks')
        self.check_for_param_presence('volname', self.section_dict)
        Global.playbooks.append('gluster-remove-brick.yml')


    def gfs_rebalance(self):
        if 'state' not in self.section_dict:
            print "Error: State of the rebalance process not " \
                "specified. Can't proceed!\n" \
                "Available options are: {start, stop, fix-layout}."
            self.cleanup_and_quit()
        if 'gluster-volume-start.yml' not in Global.playbooks:
            Global.playbooks.append('gluster-volume-start.yml')
        Global.playbooks.append('gluster-volume-rebalance.yml')



