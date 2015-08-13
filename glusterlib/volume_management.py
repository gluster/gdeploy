
#!/usr/bin/python # -*- coding: utf-8 -*-
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
        self.hosts = self.config_get_options(self.config, 'hosts', False)
        try:
            self.section_dict = self.config._sections['volume']
            del self.section_dict['__name__']
        except KeyError:
            return
        action = self.section_dict.get('action') or 'create'
        self.fix_format_of_values_in_config(self.section_dict, 'transport')
        { 'create': self.create_volume,
          'delete': self.delete_volume,
          'add-brick': self.add_brick_to_volume,
          'remove-brick': self.remove_brick_from_volume,
          'rebalance': self.gfs_rebalance
        }[action]()
        if not self.hosts:
            self.split_volname_and_hostname(self.section_dict['volname'])
        self.filename = Global.group_file
        self.iterate_dicts_and_yaml_write(self.section_dict)

    def write_brick_dirs(self):
        '''
        host_var files are to be created if multiple hosts
        have different brick_dirs for gluster volume
        '''
        if self.filetype == 'group_vars':
            if not self.present_in_yaml(Global.group_file, 'mountpoints'):
                self.filename = Global.group_file
                brick_dirs = self.get_options('brick_dirs', True)
                self.create_yaml_dict('mountpoints', brick_dirs, False)
        else:
            for host in self.hosts:
                self.filename = self.get_file_dir_path(Global.host_vars_dir, host)
                if not self.present_in_yaml(self.filename, 'mountpoints'):
                    self.touch_file(self.filename)
                    brick_dirs = self.get_options('brick_dirs', True)
                    self.create_yaml_dict('mountpoints', brick_dirs, False)

    def create_volume(self):
        if not self.hosts:
            print "Error: Hostnames not provided. Cannot continue!"
            self.cleanup_and_quit()
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
        Global.playbooks.append('gluster-volume-create.yml')


    def delete_volume(self):
        self.check_for_param_presence('volname', self.section_dict)
        Global.playbooks.append('gluster-volume-delete.yml')

    def add_brick_to_volume(self):
        self.check_for_param_presence('bricks', self.section_dict)
        self.section_dict['new_bricks'] = self.section_dict.pop('bricks')
        self.check_for_param_presence('volname', self.section_dict)
        Global.playbooks.append('gluster-add-brick.yml')

    def remove_brick_from_volume(self):
        self.check_for_param_presence('bricks', self.section_dict)
        if 'state' not in self.section_dict:
            print "Error: State of the volume after remove-brick not " \
                "specified. Can't proceed!"
            self.cleanup_and_quit()
        sections_default_value = {'replica': 'no', 'replica_count': 0}
        self.set_default_value_for_dict_key(self.section_dict,
                                            sections_default_value)
        self.section_dict['old_bricks'] = self.section_dict.pop('bricks')
        self.check_for_param_presence('volname', self.section_dict)
        Global.playbooks.append('gluster-remove-brick.yml')


    def gfs_rebalance(self):
        return



