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

class GlusterConfWriter(YamlWriter):


    def parse_gluster_info(self, config):
        self.config = config
        self.filename = Global.group_file
        sections = self.config_get_sections(self.config)
        '''
        Each section in the group_sections list will be read from the conf
        stripped to get multiple or singleton entries and written
        to the groupvars file.
        Make sure to add any new section(feature) to the group_sections list
        and write a custom method which can be assigned to feature func to
        customize the data
        '''
        group_sections = [ 'volume', 'clients', 'snapshot']
        for section in group_sections:
            '''
            This try construct will make sure to continue if the
            section is absent
            '''
            try:
                option_dict = self.config._sections[section]
            except:
                continue
            del option_dict['__name__']
            for key, value in option_dict.iteritems():
                '''
                HACK: The value for option 'transport' can have comma in it,
                eg: tcp,rdma. so comma here doesn't mean that it can have
                multiple values
                '''
                if ',' in str(value) and key not in ['transport']:
                    option_dict[key] = self.split_comma_seperated_options(value)
            '''
            Custom methods for each of the feature to be added is written here.
            '''
            feature_func= { 'volume': self.write_volume_conf_data,
                            'clients': self.gluster_volume_mount,
                            'snapshot': self.snapshot_conf_write
                          }.get(section)
            if feature_func:
                option_dict = feature_func(option_dict)

            self.filename = Global.group_file
            self.iterate_dicts_and_yaml_write(option_dict)


    def gluster_volume_mount(self, client_info):
        #Custom method to write client information
        '''
        This default value dictionary is used to populate the group var
        with default data, if the data is not given by the user/
        '''
        sections_default_value = {'client_mount_points': '/mnt/gluster',
                'fstype': 'glusterfs'}
        self.set_default_value_for_dict_key(client_info,
                sections_default_value)
        self.clients = client_info['hosts']
        if not self.clients:
            return
        if type(self.clients) is str:
            self.clients = [self.clients]
        self.write_config('clients', self.clients, Global.inventory)
        del client_info['hosts']
        Global.do_volume_mount = True
        '''
        client hostnames or IP should also be in the inventory file since
        mounting is to be done in the client host machines
        '''
        if not Global.do_volume_create:
            client_info['volname'] = self.config_section_map(self.config, 'clients',
                    'volname', True)
        '''
        host_var files are to be created if multiple clients
        have different mount points for gluster volume
        '''
        for key, value in client_info.iteritems():
            gluster = dict()
            if type(value) is list:
                if len(value) != len(self.clients):
                    print "Error: Provide %s in each client " \
                            "or a common one for all the clients. " % key
                    self.cleanup_and_quit()
                for client, conf in zip(self.clients, value):
                    self.filename = self.get_file_dir_path(
                            Global.host_vars_dir, client)
                    gluster[key] = conf
                    self.iterate_dicts_and_yaml_write(gluster)
                del client_info[key]
        return client_info


    def write_volume_conf_data(self, volume_confs):
        Global.do_volume_create = True
        '''
        This default value dictionary is used to populate the group var
        with default data, if the data is not given by the user/
        '''
        sections_default_value = {'volname': 'glustervol', 'transport': 'tcp',
                'replica': 'no', 'disperse': 'no', 'replica_count': 0,
                'arbiter_count': 0, 'disperse_count': 0, 'redundancy_count': 0 }
        self.set_default_value_for_dict_key(volume_confs,
                sections_default_value)
        #Custom method for volume config specs
        if volume_confs['replica'].lower() == 'yes' and int(volume_confs[
                'replica_count']) == 0:
            print "Error: Provide the replica count for the volume."
            self.cleanup_and_quit()
        return volume_confs

    def snapshot_conf_write(self, snapshot_conf):
        '''
        Custom method to make sure snapshot works fine with the
        data read from the config file
        '''
        Global.create_snapshot = True
        if not (Global.do_volume_create or Global.do_volume_mount):
            snapshot_conf['volname'] = self.config_section_map(self.config,
                    'snapshot', 'volname', True)
        return snapshot_conf
