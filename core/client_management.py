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

from lib import *


class ClientManagement(YamlWriter):

    def __init__(self):
        self.filename = Global.group_file
        self.get_client_data()
        self.remove_from_sections('clients')


    def get_client_data(self):
        try:
            self.section_dict = self.config._sections['clients']
            del self.section_dict['__name__']
        except KeyError:
            return
        Global.logger.info("Reading client section in config")
        self.action = self.section_dict.get('action')
        if not self.action:
            msg = "Section 'clients' without any action option " \
                    "found. Skipping this section!"
            print "\nWarning: " + msg
            Global.logger.warning(msg)
            return
        del self.section_dict['action']
        self.format_client_data()


    def format_client_data(self):
        self.section_dict = self.fix_format_of_values_in_config(self.section_dict)
        self.clients =  self.section_dict.get('hosts')
        if not self.clients:
            msg = "Client hostnames not provided. Exiting!"
            print "\nError: " + msg
            Global.logger.error(msg)
            self.cleanup_and_quit()
        '''
        Supporting patterns for client hosts and client_mount_points only
        in clients section.
        '''
        self.clients = self.pattern_stripping(self.clients)
        client_mount_points = self.section_dict.get('client_mount_points')
        if client_mount_points:
            client_points = self.pattern_stripping( client_mount_points)
            '''
            HACK: If the client_points list is singleton, further methods
            expect it to be a string rather than a list
            '''
            if len(client_points) == 1:
                self.section_dict['client_mount_points'] = client_points[0]
            else:
                self.section_dict['client_mount_points'] = client_points

        '''
        client hostnames or IP should also be in the inventory file since
        mounting is to be done in the client host machines
        '''
        self.write_config('clients', self.clients, Global.inventory)


        del self.section_dict['hosts']

        action_func = { 'mount': self.mount_volume,
                        'unmount': self.unmount_volume,
                      }.get(self.action)
        if not action_func:
            msg = "Unknown action provided for client section. Exiting!\n " \
                    "Use either `mount` " \
                    "or `unmount`."
            print "\nError: " + msg
            Global.logger.error(msg)
            self.cleanup_and_quit()
        action_func()

        self.write_client_info(self.action)
        self.filename = Global.group_file


    def write_client_info(self, action):
        '''
        host_var files are to be created if multiple clients
        have different mount points for gluster volume
        '''
        '''
        This nfs-clients and fuse-clients distinction is used only for
        the mount option. Separate playbooks are run is each case as nfs
        has an extra parameter version
        '''
        self.nfs_clients = []
        self.fuse_clients = []
        self.cifs_clients = []
        for key, value in self.section_dict.iteritems():
            gluster = dict()
            if isinstance(value, list):
                if len(value) != len(self.clients):
                    msg = "Provide %s in each client " \
                        "or a common one for all the clients. " % key
                    print "\nError: " + msg
                    Global.logger.error(msg)
                    self.cleanup_and_quit()
                for client, conf in zip(self.clients, value):
                    self.filename = self.get_file_dir_path(
                        Global.host_vars_dir, client)
                    if key == 'fstype' and action == 'mount':
                        gluster = self.client_fstype_listing(conf, client)
                    else:
                        gluster[key] = conf
                del self.section_dict[key]
        if action == 'mount':
            '''
            If fstype option still exist in the config, then fstype is common
            to all the clients. For that the following.
            '''
            if 'fstype' in self.section_dict:
                if isinstance(self.clients, list):
                    self.nfs_clients += self.clients
                    self.fuse_clients += self.clients
                    self.cifs_clients += self.clients
                else:
                    self.nfs_clients.append(self.clients)
                    self.fuse_clients.append(self.clients)
                    self.cifs_clients.append(self.clients)
                self.section_dict = self.fstype_validation(self.section_dict)
            self.write_config('nfs_clients', self.nfs_clients, Global.inventory)
            self.write_config('fuse_clients', self.fuse_clients, Global.inventory)
            self.write_config('cifs_clients', self.fuse_clients, Global.inventory)


    def client_fstype_listing(self, conf, client):
        filetype_conf = {'fstype': conf, 'nfsversion': self.section_dict.get('nfs-version')}
        gluster = self.fstype_validation(filetype_conf)
        if conf == 'nfs':
            self.nfs_clients.append(client)
        elif conf == 'cifs':
            self.cifs_clients.append(client)
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
            msg = "NFS mount of volume triggered."
            print "\nINFO: " + msg
            Global.logger.info(msg)
            self.run_playbook('gluster-client-nfs-mount.yml')
        elif section_dict['fstype'] == 'glusterfs':
            msg = "FUSE mount of volume triggered."
            print "\nINFO: " + msg
            Global.logger.info(msg)
            self.run_playbook('gluster-client-fuse-mount.yml')
        elif section_dict['fstype'] == 'cifs':
            msg = "CIFS mount of volume triggered."
            if not self.present_in_yaml(
                    Global.group_file, 'smb_username') or not self.present_in_yaml(
                            Global.group_file, 'smb_password'):
                print "\nError: Provide the SMB username and password under "\
                "the 'volume' section."
                self.cleanup_and_quit()
            print "\nINFO: " + msg
            Global.logger.info(msg)
            self.run_playbook('gluster-client-cifs-mount.yml')
        else:
            msg = "Unsupported mount type. Exiting!"
            print "\nError: " + msg
            Global.logger.error(msg)
            self.cleanup_and_quit()
        return section_dict

    def mount_volume(self):
        '''
        This default value dictionary is used to populate the group var
        with default data, if the data is not given by the user/
        '''
        if not self.present_in_yaml(Global.group_file, 'volname'):
            self.check_for_param_presence('volname', self.section_dict)
        default_fstype = 'nfs' if self.config.has_section(
                'nfs-ganesha') else 'glusterfs'
        sections_default_value = {'client_mount_points': '/mnt/gluster',
                                  'fstype': default_fstype }
        self.set_default_value_for_dict_key(self.section_dict,
                                            sections_default_value)


    def unmount_volume(self):
        self.check_for_param_presence('client_mount_points',
                self.section_dict)
        self.run_playbook('client_volume_umount.yml')
        msg = "Client management(action: unmount) triggered."
        print "\nINFO: " + msg
        Global.logger.info(msg)
