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
        self.get_ganesha_data()


    def get_ganesha_data(self):
        try:
            self.section_dict = self.config._sections['nfs-ganesha']
            del self.section_dict['__name__']
        except:
            return
        action = self.section_dict.get('action')
        if not action:
            print "\nWarning: Section 'nfs-ganesha' without any action option " \
                    "found. Skipping this section!"
            return
        del self.section_dict['action']
        self.section_dict = self.fix_format_of_values_in_config(self.section_dict)
        self.get_cluster_nodes()
        action_func = { 'create-cluster': self.create_cluster,
                        'destroy-cluster': self.destroy_cluster,
                        'export-volume': self.export_volume,
                        'unexport-volume': self.unexport_volume,
                        'add-node': self.add_node,
                        'delete-node': self.delete_node
                      }[action]
        if not action_func:
            print "\nError: Unknown action provided for nfs-ganesha. Exiting!\n"\
                    "Supported actions are: [create-cluster, destroy-cluster,"\
                    "export-volume, unexport-volume]"
            self.cleanup_and_quit()
        action_func()
        self.filename = Global.group_file
        msg = "NFS-Ganesha management(action: %s) triggered" % action
        print "\nINFO: " + msg
        Global.logger.info(msg)
        self.create_yaml_dict('base_dir', Global.base_dir, False)
        self.create_yaml_dict('ha_base_dir', '/etc/ganesha', False)
        self.iterate_dicts_and_yaml_write(self.section_dict)


    def get_cluster_nodes(self):
        cluster = []
        self.check_for_param_presence('cluster-nodes', self.section_dict)
        cluster_nodes = self.section_dict.get('cluster-nodes')
        self.cluster = self.pattern_stripping(cluster_nodes)
        if Global.hosts:
            if not set(self.cluster).issubset(set(Global.hosts)):
                print "\nError: 'cluster_nodes' for nfs-ganesha should be " \
                       "subset of the 'hosts'. Exiting!"
                self.cleanup_and_quit()
        else:
            Global.hosts = self.cluster

        self.write_config('cluster_nodes', self.cluster, Global.inventory)
        self.write_config('master_node', [self.cluster[0]], Global.inventory)
        self.section_dict['cluster_hosts'] = ','.join(node for node in
                self.cluster)
        self.section_dict['master_node'] = self.cluster[0]


    def create_cluster(self):
        if not self.section_dict['ha-name']:
            self.section_dict['ha_name'] = 'ganesha-ha-360'
        else:
            self.section_dict['ha_name'] = self.section_dict.pop('ha-name')

        self.get_host_vips(self.cluster)

        if not self.section_dict.get('volname'
                ) and not self.present_in_yaml(Global.group_file, 'volname'):
            print "'volname' not provided. Exiting!"
            self.cleanup_and_quit()
        Global.playbooks.append('bootstrap-nfs-ganesha.yml')
        Global.playbooks.append('generate-public-key.yml')
        Global.playbooks.append('copy-ssh-key.yml')
        Global.playbooks.append('set-pcs-auth-passwd.yml')
        Global.playbooks.append('pcs-authentication.yml')
        Global.playbooks.append('gluster-shared-volume-mount.yml')
        Global.playbooks.append('ganesha-conf-create.yml')
        Global.playbooks.append('enable-nfs-ganesha.yml')
        self.export_volume()


    def get_host_vips(self, cluster):
        self.check_for_param_presence('vip', self.section_dict)
        VIPs = self.pattern_stripping(self.section_dict.get('vip'))
        if len(cluster) != len(VIPs):
            print "\nError: The number of cluster_nodes provided and VIP "\
                    "given doesn't match. Exiting!"
            self.cleanup_and_quit()
        self.section_dict['vip'] = VIPs
        vip_list = []
        for host, vip in zip(cluster, VIPs):
            key = 'VIP_' + host
            vip_list.append("%s=\"%s\"" %(key, vip))
        VIPs = '\n'.join(vip_list)
        self.section_dict['vip_list'] = VIPs

    def export_volume(self):
        if not self.section_dict.get('volname'
                ) and not self.present_in_yaml(Global.group_file, 'volname'):
            print "'volname' not provided. Exiting!"
            self.cleanup_and_quit()
        self.section_dict['value'] = "on"
        Global.playbooks.append('ganesha-volume-configs.yml')
        Global.playbooks.append('gluster-volume-export-ganesha.yml')

    def destroy_cluster(self):
        Global.playbooks.append('disable-nfs-ganesha.yml')

    def unexport_volume(self):
        if not self.section_dict.get('volname'
                ) and not self.present_in_yaml(Global.group_file, 'volname'):
            print "'volname' not provided. Exiting!"
            self.cleanup_and_quit()
        self.section_dict['value'] = "off"
        Global.playbooks.append('gluster-volume-export-ganesha.yml')
        return

    def add_node(self):
        self.check_for_param_presence('nodes', self.section_dict)
        new_nodes = self.section_dict.get('nodes')
        nodes = self.pattern_stripping(new_nodes)
        self.get_host_vips(nodes)
        for node, vip in zip(nodes, self.section_dict['vips']):
            nodes_list = {}
            nodes_list['host'] = node
            nodes_list['vip'] = vip
            data.append(nodes_list)
        self.create_yaml_dict('nodes_list', data, True)
        Global.playbooks.append('bootstrap-nfs-ganesha.yml')
        Global.playbooks.append('ganesha-cluster-add.yml')

    def delete_node(self):
        self.check_for_param_presence('nodes', self.section_dict)
        new_nodes = self.section_dict.get('nodes')
        nodes = self.pattern_stripping(new_nodes)
        self.section_dict['nodes'] = nodes
        Global.playbooks.append('ganesha-cluster-delete.yml')
