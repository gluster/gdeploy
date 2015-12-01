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
        self.section_dict = self.fix_format_of_values_in_config(self.section_dict)
        sections_default_value = {'zone': 'public',
                                  'permanent': 'true'
                                  }
        self.set_default_value_for_dict_key(self.section_dict,
                                            sections_default_value)
        firewalld_op = re.match('(.*)-(.*)', action)
        if firewalld_op:
            if firewalld_op.group(1) == 'add':
                self.add_ports()
            elif firewalld_op.group(1) == 'delete':
                self.delete_ports()
            else:
                self.wrong_action()
            if firewalld_op.group(2) == 'services':
                self.service_action()
            elif firewalld_op.group(2) == 'ports':
                self.port_action()
            else:
                self.wrong_action()
        else:
            self.wrong_action()
        if not Global.hosts:
            print "Error: Hostnames not provided. Cannot continue!"
            self.cleanup_and_quit()
        self.filename = Global.group_file
        print "\nINFO: Firewalld management(action: %s) triggered" % action
        self.iterate_dicts_and_yaml_write(self.section_dict)


    def wrong_action(self):
        print "Error: Unknown action for firewalld.\n Supported actions " \
                "are: [add-ports, delete-ports, add-services, " \
                "delete-services]. Exiting!"
        self.cleanup_and_quit()

    def add_ports(self):
        self.section_dict['firewall_state'] = 'enabled'

    def delete_ports(self):
        self.section_dict['firewall_state'] = 'disabled'

    def service_action(self):
        if 'service' in self.section_dict:
            Global.playbooks.append('firewalld-service-op.yml')
        else:
            print "\nError: provide 'services' in " \
                "firewalld section"
            self.cleanup_and_quit()

    def port_action(self):
        if 'ports' in self.section_dict:
            Global.playbooks.append('firewalld-ports-op.yml')
        else:
            print "\nError: provide 'ports' in " \
                "firewalld section"
            self.cleanup_and_quit()
