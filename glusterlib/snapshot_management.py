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


class SnapshotManagement(YamlWriter):

    def __init__(self, config):
        self.config = config
        try:
            self.section_dict = self.config._sections['snapshot']
            del self.section_dict['__name__']
        except KeyError:
            return
        action = self.section_dict.get('action')
        self.fix_format_of_values_in_config(self.section_dict)
        action_func =  {'create': self.snapshot_create,
                         'delete': self.snapshot_delete,
                         'config': self.snapshot_config,
                         'restore': self.snapshot_restore,
                         'clone': self.snapshot_clone,
                         'activate': self.snapshot_activate,
                         'deactivate': self.snapshot_deactivate
                        }[action]
        if not action_func:
            print "Error: Unknown action for snapshot.\n Supported actions " \
                    "are: [create, delete, config, restore, clone]. Exiting!"
            self.cleanup_and_quit()
        action_func()
        if not Global.hosts:
            print "Error: Hostnames not provided. Cannot continue!"
            self.cleanup_and_quit()
        self.filename = Global.group_file
        print "INFO: Snapshot management(action: %s) triggered" % action
        self.iterate_dicts_and_yaml_write(self.section_dict)

    def snapshot_create(self):
        if self.config.has_section('volume'):
            if self.config_section_map('volume', 'action', False) == 'create':
                print "warning: looks like you are just creating your volume. \ncreating a" \
                    "snapshot now doesn't make much sense. skipping snapshot "\
                    "section."
                return
        if not self.present_in_yaml(Global.group_file, 'volname'):
            self.check_for_param_presence('volname', self.section_dict)
        if not self.section_dict.get('snapname'):
            self.section_dict['snapname'] = self.section_dict['volname'] + '_snap'
        Global.playbooks.append('gluster-snapshot-create.yml')


    def snapshot_delete(self):
        if not self.section_dict['snapname'] and not self.section_dict['volname']:
            print "Error: snapname or volname not provided for snapshot " \
                    "delete option. Exiting!"
            self.cleanup_and_quit()
        sections_default_value = {
                'snapname': None,
                'volname': None }
        self.set_default_value_for_dict_key(self.section_dict,
                                            sections_default_value)
        Global.playbooks.append('gluster-snapshot-delete.yml')

    def snapshot_clone(self):
        self.check_for_param_presence('snapname', self.section_dict)
        self.check_for_param_presence('clonename', self.section_dict)
        Global.playbooks.append('gluster-snapshot-clone.yml')

    def snapshot_restore(self):
        self.check_for_param_presence('snapname', self.section_dict)
        Global.playbooks.append('gluster-snapshot-restore.yml')

    def snapshot_activate(self):
        self.check_for_param_presence('snapname', self.section_dict)
        if not self.section_dict.get('force'):
            self.section_dict['force'] = 'no'
        Global.playbooks.append('gluster-snapshot-activate.yml')

    def snapshot_deactivate(self):
        self.check_for_param_presence('snapname', self.section_dict)
        Global.playbooks.append('gluster-snapshot-deactivate.yml')


    def snapshot_config(self):
        sections_default_value = {'snap_max_soft_limit': None,
                                  'volname': None,
                                  'snap_max_hard_limit': None,
                                  'auto_delete': None,
                                  'activate_on_create': None
                                  }
        self.set_default_value_for_dict_key(snap_conf,
                                            sections_default_value)
        Global.playbooks.append('gluster-snapshot-config.yml')
