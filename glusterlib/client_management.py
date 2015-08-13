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


class ClientManagement(YamlWriter):

    def __init__(self, config):
        self.config = config
        try:
            self.section_dict = self.config._sections['client']
            del self.section_dict['__name__']
        except KeyError:
            return
        action = self.section_dict.get('action') or 'mount'
        self.fix_format_of_values_in_config(self.section_dict)
        self.clients =  self.section_dict,get('hosts')
        if not self.clients:
            return
        '''
        client hostnames or IP should also be in the inventory file since
        mounting is to be done in the client host machines
        '''
        self.write_config('clients', self.clients, Global.inventory)
        del self.section_dict['hosts']
        '''
        HACK: The format of the clients gets distorted if it is a single
        client host, as the config_parser returns a str instead of list
        '''
        if isinstance(self.clients, str):
            self.clients = [self.clients]
        { 'mount': self.mount_volume,
          'unmount': self.unmount_volume,
        }[self.section_dict(action)]()
        self.write_client_info()


    def write_client_info(self):
        '''
        host_var files are to be created if multiple clients
        have different mount points for gluster volume
        '''
        for key, value in self.section_dict.iteritems():
            gluster = dict()
            if isinstance(value, list):
                if len(value) != len(self.clients):
                    print "Error: Provide %s in each client " \
                        "or a common one for all the clients. " % key
                    self.cleanup_and_quit()
                for client, conf in zip(self.clients, value):
                    self.filename = self.get_file_dir_path(
                        Global.host_vars_dir, client)
                    gluster[key] = conf
                    self.iterate_dicts_and_yaml_write(gluster)
                del self.section_dict[key]

    def mount_volume(self):
        '''
        This default value dictionary is used to populate the group var
        with default data, if the data is not given by the user/
        '''
        self.check_for_param_presence('volname', self.section_dict)
        sections_default_value = {'client_mount_points': '/mnt/gluster',
                                  'fstype': 'glusterfs'}
        self.set_default_value_for_dict_key(client_info,
                                            sections_default_value)
        if self.section_dict['fstype'] == 'nfs':
            if not client_info.get('nfs-version'):
                conf_dict['nfs-version'] = 3
            Global.playbooks.append('gluster-client-nfs-mount.yml')
        elif self.section_dict['fstype'] == 'glusterfs':
            Global.playbooks.append('gluster-client-fuse-mount.yml')
        else:
            print "Error: Unsupported mount type. Exiting!"
            self.cleanup_and_quit()


    def unmount_volume(self):
        self.check_for_param_presence('client_mount_points', self.section_dict)
        Global.playbooks.append('client_volume_umount.yml')
