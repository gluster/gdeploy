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
from collections import OrderedDict
import re


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
        group_sections = ['volume', 'clients', 'snapshot', 'nfs-ganesha']
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
                    option_dict[
                        key] = self.split_comma_seperated_options(value)
            '''
            Custom methods for each of the feature to be added is written here.
            '''
            feature_func = OrderedDict([
                ('volume', self.write_volume_conf_data),
                ('nfs-ganesha', self.ganesha_conf_write),
                ('clients', self.write_client_conf_data),
                ('snapshot', self.snapshot_conf_write)
            ]).get(section)
            if feature_func:
                option_dict = feature_func(option_dict)
            '''
            If the user has given the volname in the format
            <hostname>:<volname>, this will be handy
            '''
            if option_dict.get('volname'):
                option_dict['volname'] = self.split_volname_and_hostname(
                    option_dict['volname'])
            self.filename = Global.group_file
            self.iterate_dicts_and_yaml_write(option_dict)

    def write_client_conf_data(self, client_info):
        # Custom method to write client information
        self.clients = client_info['hosts']
        if not self.clients:
            return
        if isinstance(self.clients, str):
            self.clients = [self.clients]
        '''
        client hostnames or IP should also be in the inventory file since
        mounting is to be done in the client host machines
        '''
        self.write_config('clients', self.clients, Global.inventory)
        del client_info['hosts']
        if client_info.get('action') in ['mount']:
            '''
            This default value dictionary is used to populate the group var
            with default data, if the data is not given by the user/
            '''
            sections_default_value = {'client_mount_points': '/mnt/gluster'}
            section_default_value['\
                    fstype'] = 'nfs' if Global.setup_ganesha else 'glsuterfs'
            self.set_default_value_for_dict_key(client_info,
                                                sections_default_value)
            if client_info['fstype'] == 'nfs':
                Global.do_nfs_mount = True
                if not client_info.get('nfs-version'):
                    conf_dict['nfs-version'] = 3
            else:
                Global.do_fuse_mount = True
            self.check_presence_of_volname(client_info)

        elif client_info.get('action') == 'unmount':
            Global.do_volume_umount = True
            if not client_info.get('client_mount_points'):
                print "Error: No 'client_mount_points' provided. Exiting!"
                self.cleanup_and_quit()
        '''
        host_var files are to be created if multiple clients
        have different mount points for gluster volume
        '''
        for key, value in client_info.iteritems():
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
                del client_info[key]

        return client_info

    def write_volume_conf_data(self, volume_confs):
        if volume_confs.get('action') == 'delete':
            Global.do_volume_delete = True
            return volume_confs

        # This takes in the parameters needed for volume create
        if volume_confs.get('action') == 'create':
            volume_confs = self.volume_create_conf_write(volume_confs)

        if volume_confs.get('action') in ['add-brick', 'remove-brick']:
            volume_confs = self.volume_brick_change_conf_write(volume_confs)

        if 'volname' not in volume_confs:
            print "Error: Name of the volume('volname') not provided in 'volume' " \
                "section. Can't proceed!"
            self.cleanup_and_quit()

        return volume_confs

    def split_volname_and_hostname(self, volname):
        '''
        This gives the user the flexibility to not give the hosts
        section. Instead one can just specify the volume name
        with one of the peer member's hostname or IP in the
        format <hostname>:<volumename>
        '''
        vol_group = re.match("(.*):(.*)", volname)
        if vol_group:
            Global.master = [vol_group.group(1)]
            return vol_group.group(2)
        return volname

    def volume_create_conf_write(self, volume_confs):
        Global.do_volume_create = True
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
        self.set_default_value_for_dict_key(volume_confs,
                                            sections_default_value)
        # Custom method for volume config specs
        if volume_confs['replica'].lower() == 'yes' and int(volume_confs[
                'replica_count']) == 0:
            print "Error: Provide the replica count for the volume."
            self.cleanup_and_quit()
        return volume_confs

    def volume_brick_change_conf_write(self, volume_confs):
        if 'bricks' not in volume_confs:
            print "Error: The name of the brick(s) not " \
                "specified. Can't proceed!"
            self.cleanup_and_quit()
        if volume_confs.get('action') == 'add-brick':
            volume_confs['new_bricks'] = volume_confs.pop('bricks')
            Global.volume_add_brick = True
        if volume_confs.get('action') == 'remove-brick':
            if 'state' not in volume_confs:
                print "Error: State of the volume after remove-brick not " \
                    "specified. Can't proceed!"
                self.cleanup_and_quit()
            sections_default_value = {'replica': 'no', 'replica_count': 0}
            self.set_default_value_for_dict_key(volume_confs,
                                                sections_default_value)
            volume_confs['old_bricks'] = volume_confs.pop('bricks')
            Global.volume_remove_brick = True
        return volume_confs

    def snapshot_conf_write(self, snap_conf):
        '''
        custom method to make sure snapshot works fine with the
        data read from the config file
        '''
        if snap_conf.get('action') in ['create']:
            if Global.do_volume_create:
                print "warning: looks like you are just creating your volume. creating a" \
                    "snapshot now doesn't make much sense. skipping snapshot "\
                    "section."
                return snap_conf
            Global.create_snapshot = True
            self.check_presence_of_volname(snap_conf)
            if not snap_conf.get('snapname'):
                snap_conf['snapname'] = snap_conf['volname'] + '_snap'
        elif snap_conf.get('action') == 'config':
            Global.config_snapshot = True
            sections_default_value = {'snap_max_soft_limit': None,
                                      'volname': None,
                                      'snap_max_hard_limit': None,
                                      'auto_delete': None,
                                      'activate_on_create': None
                                      }
            self.set_default_value_for_dict_key(snap_conf,
                                                sections_default_value)
        else:
            if snap_conf.get('action') == 'delete':
                Global.delete_snapshot = True
            if snap_conf.get('action') == 'clone':
                Global.clone_snapshot = True
                if not snap_conf.get('clonename'):
                    print "error: clonename not specified. exiting!"
                    self.cleanup_and_quit()
            if snap_conf.get('action') == 'restore':
                Global.restore_snapshot = True
            if not snap_conf.get('snapname'):
                print "error: snapname not specified. exiting!"
                self.cleanup_and_quit()
        return snap_conf

    def ganesha_conf_write(self, conf_dict):
        if conf_dict.get('action') == 'create':
            cluster_nodes = conf_dict['cluster-nodes']
            self.write_config('cluster_nodes', cluster_nodes, Global.inventory)
            self.write_config('master_node', [cluster_nodes[0]], Global.inventory)
            Global.setup_ganesha = True
        elif conf_dict.get('action') == 'destroy-cluster':
            Global.destroy_cluster = True
        elif conf_dict.get('action') == 'unexport-volume':
            Global.unexport_volume = True
        if self.present_in_yaml(self.filename, 'volname'
                                    ) or conf_dict['volname']:
            Global.export_volume = True
        return conf_dict

    def check_presence_of_volname(self, conf_dict):
        if not self.present_in_yaml(self.filename, 'volname'
                                    ) and not conf_dict['volname']:
            print "Error: 'volname' not specified. Exiting!"
            self.cleanup_and_quit()
