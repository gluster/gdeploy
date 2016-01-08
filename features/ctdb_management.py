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
import re


class CtdbManagement(YamlWriter):

    def __init__(self, config):
        self.config = config
        try:
            self.section_dict = self.config._sections['ctdb']
            del self.section_dict['__name__']
        except KeyError:
            return
        self.get_ctdb_data()


    def get_ctdb_data(self):
        action = self.section_dict.get('action')
        if not action:
            print "Warning: Section 'ctdb' without any action option " \
                    "found. Skipping this section!"
            return
        del self.section_dict['action']
        if not Global.hosts:
            print "Error: Hostnames not provided. Cannot continue!"
            self.cleanup_and_quit()
        self.section_dict = self.fix_format_of_values_in_config(
                self.section_dict)
        action_func =  {'setup': self.setup_ctdb,
                        'start': self.start_ctdb,
                        'enable': self.enable_ctdb,
                        'stop': self.stop_ctdb,
                        'disable': self.disable_ctdb
                        }.get(action)
        if not action_func:
            print "Error: Unknown action for snapshot.\n Supported actions " \
                    "are: [setup, start, enable, stop, disable]. Exiting!"
            self.cleanup_and_quit()
        action_func()
        self.filename = Global.group_file
        print "\nINFO: CTDB management(action: %s) triggered" % action
        self.iterate_dicts_and_yaml_write(self.section_dict)


    def setup_ctdb(self):
        sections_default_value = {
                'CTDB_PUBLIC_ADDRESSES': '/etc/ctdb/public_addresses',
                'CTDB_NODES': '/etc/ctdb/nodes',
                'CTDB_MANAGES_SAMBA': 'no',
                'CTDB_RECOVERY_LOCK': '/mnt/lock/reclock'
            }
        self.set_default_value_for_dict_key(self.section_dict,
                                            sections_default_value)
        option = ''
        pattern = '^CTDB_.*'
        opt_matches = [opt for opt in list(self.section_dict) if
                re.search(pattern, opt)]
        for key in opt_matches:
            if self.section_dict[key] and self.section_dict[key].lower() != 'none':
                option += key + '=' + str(self.section_dict[key]) + '\n'

        self.section_dict['options'] = option
        self.section_dict['nodes'] = '\n'.join(Global.hosts)
        paddress = self.section_dict.get('public_address')
        if paddress:
            if not isinstance(paddress, list):
                paddress= [paddress]
            if not isinstance(paddress, list):
                paddress = [paddress]
            paddress = self.pattern_stripping(paddress)
            paddress_list = map(lambda x: x.split(' '), paddress)
            paddress_list = filter(None, paddress_list)
            addresses, interfaces = [], []
            for ip in paddress_list:
                addresses.append(ip[0])
                try:
                    interfaces.append(ip[1])
                except:
                    interfaces.append(' ')
            addresses = self.pattern_stripping(addresses)
            interfaces = map(lambda x: x.replace(';',','), interfaces)
            paddress = []
            for ip, inter in zip(addresses, interfaces):
                public_add = ip + ' ' + inter
                paddress.append(public_add)
            self.section_dict['paddress'] = '\n'.join(paddress)
        Global.playbooks.append('setup_ctdb.yml')
        self.start_ctdb()
        self.enable_ctdb()

    def start_ctdb(self):
        self.section_dict['service'] = ['ctdb']
        self.section_dict['state'] = 'started'
        Global.playbooks.append('service_management.yml')
        return

    def stop_ctdb(self):
        self.section_dict['service'] = ['ctdb']
        self.section_dict['state'] = 'stopped'
        Global.playbooks.append('service_management.yml')
        return

    def enable_ctdb(self):
        self.section_dict['service'] = ['ctdb']
        self.section_dict['enabled'] = 'yes'
        Global.playbooks.append('chkconfig_service.yml')
        return

    def disable_ctdb(self):
        self.section_dict['service'] = ['ctdb']
        self.section_dict['enabled'] = 'no'
        Global.playbooks.append('chkconfig_service.yml')
        return
