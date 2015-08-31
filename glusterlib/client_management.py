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
        self.filename = Global.group_file
        try:
            self.section_dict = self.config._sections['clients']
            del self.section_dict['__name__']
        except KeyError:
            return
        action = self.section_dict.get('action')
        if not action:
            self.iterate_dicts_and_yaml_write(self.section_dict)
            return
        self.fix_format_of_values_in_config(self.section_dict)
        self.clients =  self.section_dict.get('hosts')
        if not self.clients:
            print "Error: Client hostnames not provided. Exiting!"
            self.cleanup_and_quit()
        '''
        client hostnames or IP should also be in the inventory file since
        mounting is to be done in the client host machines
        '''
        '''
        HACK: The format of the clients gets distorted if it is a single
        client host, as the config_parser returns a str instead of list
        '''
        if isinstance(self.clients, str):
            self.clients = [self.clients]
        self.write_config('clients', self.clients, Global.inventory)
        del self.section_dict['hosts']
        action_func = { 'mount': self.mount_volume,
                          'unmount': self.unmount_volume,
                        }.get(action)
        if not action_func:
            print "Error: Unknown action provided for client section. Exiting!\n " \
                    "Use either `mount` " \
                    "or `unmount`."
            self.cleanup_and_quit()
        action_func()
        self.write_client_info(action)
        self.filename = Global.group_file
        self.iterate_dicts_and_yaml_write(self.section_dict)


    def write_client_info(self, action):
        '''
        host_var files are to be created if multiple clients
        have different mount points for gluster volume
        '''
        self.nfs_clients = []
        self.fuse_clients = []
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
                    if key == 'fstype' and action == 'mount':
                        gluster = self.client_fstype_listing(conf, client)
                    else:
                        gluster[key] = conf
                    self.iterate_dicts_and_yaml_write(gluster)
                del self.section_dict[key]
        if 'fstype' in self.section_dict and action == 'mount':
            if isinstance(self.clients, list):
                self.nfs_clients += self.clients
                self.fuse_clients += self.clients
            else:
                self.nfs_clients.append(self.clients)
                self.fuse_clients.append(self.clients)
            self.section_dict = self.fstype_validation(self.section_dict)
        self.write_config('nfs_clients', self.nfs_clients, Global.inventory)
        self.write_config('fuse_clients', self.fuse_clients, Global.inventory)


    def client_fstype_listing(self, conf, client):
        filetype_conf = {'fstype': conf, 'nfsversion': self.section_dict.get('nfs-version')}
        gluster = self.fstype_validation(filetype_conf)
        if conf == 'nfs':
            self.nfs_clients.append(client)
        else:
            self.fuse_clients.append(client)
        try:
            self.section_dict.pop('nfs-version')
        except:
            pass
        return gluster

    def fstype_validation(self, section_dict):
        if section_dict['fstype'] == 'nfs':
            if not section_dict.get('nfs-version'):
                section_dict['nfsversion'] = 3
            else:
                section_dict['nfsversion'] = section_dict.pop('nfs-version')
            print "INFO: NFS mount of volume triggered."
            Global.playbooks.append('gluster-client-nfs-mount.yml')
        elif section_dict['fstype'] == 'glusterfs':
            print "INFO: FUSE mount of volume triggered."
            Global.playbooks.append('gluster-client-fuse-mount.yml')
        else:
            print "Error: Unsupported mount type. Exiting!"
            self.cleanup_and_quit()
        return section_dict

    def mount_volume(self):
        '''
        This default value dictionary is used to populate the group var
        with default data, if the data is not given by the user/
        '''
        if not self.present_in_yaml(Global.group_file, 'volname'):
            self.check_for_param_presence('volname', self.section_dict)
        sections_default_value = {'client_mount_points': '/mnt/gluster',
                                  'fstype': 'glusterfs'}
        self.set_default_value_for_dict_key(self.section_dict,
                                            sections_default_value)


    def unmount_volume(self):
        self.check_for_param_presence('client_mount_points',
                self.section_dict)
        Global.playbooks.insert(0, 'client_volume_umount.yml')
