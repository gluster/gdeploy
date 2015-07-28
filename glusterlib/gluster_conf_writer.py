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
        '''
        Each of the seperate feature to be added other than
        the back-end setup provided as a seperate section in
        the conf file should be mentioned in this list
        '''
        gluster_sections = ['volume', 'clients', 'snapshot']
        sections = self.config_get_sections(self.config)
        if 'volume' not in sections:
            gluster_sections.remove('volume')
            Global.do_volume_create = False
        if 'clients' not in sections:
            gluster_sections.remove('clients')
            Global.do_volume_mount = False
        if 'snapshot' not in sections:
            gluster_sections.remove('snapshot')
            Global.do_snapshot_create = False
        Global.do_gluster_deploy = (Global.do_volume_create and
                Global.do_volume_mount)

        '''
        The default value for options in these sections in
        case user didn't provide them should be given in
        this sections_default_value hash
        '''
        sections_default_value = dict()
        sections_default_value['clients'] = {'client_mount_points': '/mnt/gluster',
                'fstype': 'glusterfs'}
        sections_default_value['volume'] = {'volname': 'glustervol', 'transport': 'tcp',
                'replica': 'no', 'disperse': 'no', 'replica_count': 0,
                'arbiter_count': 0, 'disperse_count': 0, 'redundancy_count': 0 }

        for section in gluster_sections:
            option_dict = self.config._sections[section]
            self.set_default_value_for_dict_key(option_dict,
                    sections_default_value[section])
            del option_dict['__name__']
            for key, value in option_dict.iteritems():
                '''
                The value for option 'transport' can have comma in it,
                eg: tcp,rdma. so comma doesn't mean that it can have
                multiple values
                '''
                if ',' in str(value) and key not in ['transport']:
                    option_dict[key] = self.split_comma_seperated_options(value)
            '''
            Custom methods for each of the feature to be added is written here.
            '''
            try:
                option_dict = { 'volume': self.write_volume_conf_data,
                                'clients': self.gluster_volume_mount,
                                'snapshot': self.snapshot_conf_write
                              }[section](option_dict)
            except:
                pass

            self.filename = Global.group_file
            self.iterate_dicts_and_yaml_write(option_dict)


    def gluster_volume_mount(self, client_info):
        self.clients = client_info['hosts']
        del client_info['hosts']
        if not self.clients:
            Global.do_volume_mount = False
            return
        '''
        client hostnames or IP should also be in the inventory file since
        mounting is to be done in the client host machines
        '''
        self.write_config('clients', self.clients, Global.inventory)
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


    def snapshot_conf_write(self, snapshot_conf):
        if not (Global.do_volume_create or Global.do_volume_mount):
            snapshot_conf['volname'] = self.config_section_map(self.config,
                    'clients', 'volname', True)
            return snapshot_conf


    def write_volume_conf_data(self, volume_confs):
        if volume_confs['replica'].lower() == 'yes' and int(volume_confs[
                'replica_count']) == 0:
            print "Error: Provide the replica count for the volume."
            self.cleanup_and_quit()
        return volume_confs
