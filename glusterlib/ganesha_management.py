#!/usr/bin/python
# -*- coding: utf-8 -*- #
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


class GaneshaManagement(YamlWriter):

    def __init__(self, config):
        self.config = config
        try:
            self.section_dict = self.config._sections('nfs-ganesha')
            del self.section_dict['__name__']
        except:
            return
        action = self.section_dict.get('action')
        if not action:
            self.iterate_dicts_and_yaml_write(self.section_dict)
            return
        self.fix_format_of_values_in_config(self.section_dict)
        action_func = { 'create-cluster': self.create_cluster,
                        'destroy-cluster': self.destroy_cluster,
                        'export-volume': self.export_volume,
                        'unexport-volume': self.unexport_volume
                      }[action]
        if not action_func:
            print "Error: Unknown action provided for nfs-ganesha. Exiting!\n"\
                    "Supported actions are: [create-cluster, destroy-cluster,"\
                    "export-volume, unexport-volume]"
            self.cleanup_and_quit()
        action_func()


    def create_cluster(self):
        cluster_nodes = self.section_dict.get('cluster_nodes')
        if not cluster_nodes:
            print "Error: Option cluster_nodes not provided for nfs-ganesha." \
                    "\nCannot continue!"
            self.cleanup_and_quit()
        cluster_nodes = self.parse_patterns(cluster_nodes)
        self.write_config('cluster_nodes', cluster_nodes, Global.inventory)
        self.write_config('master_node', [cluster_nodes[0]], Global.inventory)
        Global.playbooks.append('bootstrap-nfs-ganesha.yml')
        if self.check_for_param_presence(
        'volname', False) or self.present_in_yaml(Global.group_file, 'volname'):
            self.export_volume()


    def export_volume(self):
        Global.playbooks.append('ganesha-volume-configs.yml')
        Global.playbooks.append('gluster-shared-volume-mount.yml')
        Global.playbooks.append('gluster-volume-export-ganesha.yml')

