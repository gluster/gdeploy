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
    def __init__(self, config):
        self.filename = Global.group_file
        self.config = config
        self.gluster_vol_spec()

    def gluster_vol_spec(self):
        client_info = self.config._sections['clients']
        del client_info['__name__']
        sections_default_value = {'client_mount_points': '/mnt/gluster',
                'fstype': 'glusterfs'}
        self.set_default_value_for_dict_key(client_info, sections_default_value)
        self.clients = self.split_comma_seperated_options(client_info['hosts'])
        if not self.clients:
            log_level = 'Warning' if Global.do_setup_backend else 'Error'

            print "%s: Client hosts are not specified. Cannot do GlusterFS " \
                    "deployement." % log_level
            Global.do_gluster_deploy = False
            return
        self.write_config('clients', self.clients, Global.inventory)
        if not Global.do_setup_backend:
            print "Warning: Since no brick data is provided, we cannot do a "\
                    "backend setup. Continuing with gluster deployement using "\
                    " the mount points provided"
        for key, value in client_info.iteritems():
            if ',' in value:
                client_info[key] = self.split_comma_seperated_options(value)
        self.write_volume_conf_data()
        self.write_client_conf_data(client_info)

    def write_volume_conf_data(self):
        volume_confs = self.config._sections['volume']
        del volume_confs['__name__']
        sections_default_value = {'volname': 'glustervol', 'transport': 'tcp',
                'replica': 'no', 'disperse': 'no', 'replica_count': 0,
                'arbiter_count': 0, 'disperse_count': 0, 'redundancy_count': 0 }
        self.set_default_value_for_dict_key(volume_confs, sections_default_value)
        if volume_confs['replica'].lower() == 'yes' and int(volume_confs[
                'replica_count']) == 0:
            print "Error: Provide the replica count for the volume."
            self.cleanup_and_quit()
        Global.create_snapshot = True if 'snapname' in volume_confs else False
        self.iterate_dicts_and_yaml_write(volume_confs)

    def write_client_conf_data(self, client_info):
        '''
        client hostnames or IP should also be in the inventory file since
        mounting is to be done in the client host machines
        Also, host_var files are to be created if multiple clients
        have different mount points for gluster volume
        '''
        del client_info['hosts']
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
            else:
                self.filename = Global.group_file
                gluster[key] = value
                self.iterate_dicts_and_yaml_write(gluster)
