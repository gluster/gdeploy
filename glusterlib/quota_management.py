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


class QuotaManagement(YamlWriter):

    def __init__(self, config):
        self.config = config
        try:
            self.section_dict = self.config._sections['quota']
            del self.section_dict['__name__']
        except KeyError:
            return
        self.get_quota_data()




    def get_quota_data(self):
        action = self.section_dict.get('action')
        if not action:
            print "\nWarning: Section 'quota' without any action option " \
                    "found. Skipping this section!"
            return
        self.section_dict = self.fix_format_of_values_in_config(self.section_dict)
        self.check_for_param_presence('client_hosts', self.section_dict)
        self.client_hosts = self.pattern_stripping(self.section_dict['client_hosts'])
        self.write_config('client_host', self.client_hosts, Global.inventory)
        del self.section_dict['client_hosts']


        if not self.present_in_yaml(Global.group_file, 'volname'):
            self.check_for_param_presence('volname', self.section_dict)
            self.section_dict['volname'] = self.split_val_and_hostname(
                    self.section_dict['volname'])

        sections_default_value = {
                                    'path': None,
                                    'size': None,
                                    'number': None,
                                    'percent': None,
                                    'time': None
                                }
        self.set_default_value_for_dict_key(self.section_dict,
                                            sections_default_value)


        action_func =  {
                         'default-soft-limit': self.quota_default_soft_limit,
                         'limit-usage': self.quota_limit_usage,
                         'limit-objects': self.quota_limit_objects,
                        }.get(action)

        if action in ['enable', 'disable']:
            action_func = self.dummy

        if action in ['remove', 'remove-objects']:
            action_func = self.quota_remove_action

        if action in ['alert-time', 'soft-timeout', 'hard-timeout']:
            action_func = self.quota_time_bounds

        self.section_dict['action'] = action.replace('-', '_')
        if not action_func:
            print "\nError: Unknown action for 'quota'.\n Supported actions " \
                    "are: \n[enable, disable, remove, remove-objects, " \
                    "default-soft-limit, limit-usage, limit-objects, " \
                    "alert-time, soft-timeout, hard-timeout]. \nExiting!"
            self.cleanup_and_quit()
        action_func()
        self.get_client_info()


        Global.playbooks.append('gluster-quota-ops.yml')
        self.filename = Global.group_file
        print "\nINFO: Quota management(action: %s) triggered" % action
        self.iterate_dicts_and_yaml_write(self.section_dict)


    def get_client_info(self):
        for key, value in self.section_dict.iteritems():
            gluster = dict()
            if isinstance(value, list):
                if len(value) != len(self.client_hosts):
                    print "\nError: Provide %s in each client " \
                        "or a common one for all the clients. " % key
                    self.cleanup_and_quit()
                for client, conf in zip(self.client_hosts, value):
                    self.filename = self.get_file_dir_path(
                        Global.host_vars_dir, client)
                    gluster[key] = conf
                    self.iterate_dicts_and_yaml_write(gluster)
                del self.section_dict[key]

    def dummy(self):
        return True

    def quota_default_soft_limit(self):
        self.check_for_param_presence('percent', self.section_dict)


    def quota_limit_usage(self):
        self.check_for_param_presence('path', self.section_dict)
        self.check_for_param_presence('size', self.section_dict)

    def quota_limit_objects(self):
        self.check_for_param_presence('path', self.section_dict)
        self.check_for_param_presence('number', self.section_dict)


    def quota_remove_action(self):
        self.check_for_param_presence('path', self.section_dict)


    def quota_time_bounds(self):
        self.check_for_param_presence('time', self.section_dict)
