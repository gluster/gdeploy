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

from gdeploylib import *
from gdeploylib.defaults import *


class ClientManagement(Helpers):

    def __init__(self):
        self.filename = Global.group_file
        Global.current_hosts = Global.hosts
        self.get_client_data()
        self.remove_from_sections('clients')


    def get_client_data(self):
        self.section_lists = self.get_section_dict('clients')
        if not self.section_lists:
            return
        for each in self.section_lists:
            self.section_dict = each
            del self.section_dict['__name__']
            self.client_action()

    def client_action(self):
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
        self.section_dict = self.format_values(self.section_dict)
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
        '''
        client hostnames or IP should also be in the inventory file since
        mounting is to be done in the client host machines
        '''
        self.write_config('clients', self.clients, Global.inventory)

        client_mount_points = self.section_dict.get('client_mount_points')
        if client_mount_points:
            client_mount_points = self.pattern_stripping(client_mount_points)
            if len(client_mount_points) != len(self.clients):
                if self.action == 'mount' and len(client_mount_points) == 1:
                    client_mount_points *= len(self.clients)
                else:
                    print "\nError: Number of mount points doesn't match the "\
                            "number of client hosts"
                    self.cleanup_and_quit()
            self.section_dict['client_mount_points'] = client_mount_points

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


    def mount_volume(self):
        if len(self.section_lists) > 1:
            self.section_dict['volname'] = self.get_vol_name()
        else:
            if not self.is_present_in_yaml(Global.group_file, 'volname'):
                self.section_dict['volname'] = self.get_vol_name()
        if not self.section_dict.get('client_mount_points'):
            mnt_pts = ['/mnt/client' +
                    str(i) for i in range(len(self.clients) + 1)]
        else:
            mnt_pts = self.section_dict['client_mount_points']
        if not self.section_dict.get('fstype'):
            fstype = ['glusterfs'] * len(self.clients)
        elif len(self.section_dict['fstype']) != len(self.clients):
            print "\nError: Number of filesystem types(fstype) doesn't match the "\
                    "number of client hosts"
            self.cleanup_and_quit()
        else:
            fstype = self.section_dict['fstype']
        for host, mnt, fs in zip(self.clients, mnt_pts, fstype):
            self.section_dict['client_mount_points'] = mnt
            self.section_dict['fstype'] = fs
            if fs == 'nfs':
                self.write_config('nfs_clients', [host], Global.inventory)
                if not self.section_dict.get('nfs-version'):
                    self.section_dict['nfsversion'] = 3
                else:
                    section_dict['nfsversion'] = section_dict.pop('nfs-version')
                self.run_playbook(NFSMNT_YML)
            elif fs == 'glusterfs':
                self.write_config('fuse_clients', [host], Global.inventory)
                self.run_playbook(FUSEMNT_YML)
            elif fs == 'cifs':
                self.write_config('cifs_clients', [host], Global.inventory)
                self.run_playbook(CIFSMNT_YML)
                if not self.is_present_in_yaml(
                        Global.group_file, 'smb_username') or not self.is_present_in_yaml(
                                Global.group_file, 'smb_password'):
                    print "\nError: Provide the SMB username and password under "\
                    "the 'volume' section."
                    self.cleanup_and_quit()
            else:
                print "\nError: Unknown fstype given"
                self.cleanup_and_quit()


    def get_vol_name(self):
        self.is_option_present('volname', self.section_dict, True)
        volname = self.split_volume_and_hostname(self.section_dict['volname'])
        return volname

    def unmount_volume(self):
        self.is_option_present('client_mount_points',
                            self.section_dict, True)
        for host, mnt in zip(self.clients, self.section_dict[
            'client_mount_points']):
            self.write_config('clients', [host], Global.inventory)
            self.section_dict['mountpoint'] = mnt
            self.run_playbook(VOLUMOUNT_YML)
        return

