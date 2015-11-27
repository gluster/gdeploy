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


class FirewalldManagement(YamlWriter):

    def __init__(self, config):
        self.config = config
        try:
            self.section_dict = self.config._sections['firewalld']
            del self.section_dict['__name__']
        except KeyError:
            return
        self.get_firewalld_data()


    def get_firewalld_data(self):
        action = self.section_dict.get('action')
        if action:
            del self.section_dict['action']
        self.check_for_param_presence('ports', self.section_dict)
        self.section_dict = self.fix_format_of_values_in_config(self.section_dict)
        sections_default_value = {'zone': 'public',
                                  'permanent': 'true'
                                  }
        self.set_default_value_for_dict_key(self.section_dict,
                                            sections_default_value)
        if action == 'add-ports':
            self.add_ports()
        elif action == 'delete-ports':
            self.delete_ports()
        else:
            print "Error: Unknown action for snapshot.\n Supported actions " \
                    "are: [add-ports, delete-ports]. Exiting!"
            self.cleanup_and_quit()
        if not Global.hosts:
            print "Error: Hostnames not provided. Cannot continue!"
            self.cleanup_and_quit()
        self.filename = Global.group_file
        Global.playbooks.append('firewalld-ports-op.yml')
        print "\nINFO: Firewalld management(action: %s) triggered" % action
        self.iterate_dicts_and_yaml_write(self.section_dict)


    def add_ports(self):
        self.section_dict['firewall_state'] = 'enabled'

    def delete_ports(self):
        self.section_dict['firewall_state'] = 'disabled'
