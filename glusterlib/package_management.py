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


class PackageManagement(YamlWriter):

    def __init__(self, config):
        self.config = config
        try:
            self.section_dict = self.config._sections['yum']
            del self.section_dict['__name__']
        except KeyError:
            return
        self.get_data()


    def get_data(self):
        action = ''
        try:
            action = self.section_dict.pop('action')
        except:
            pass
        repo = self.section_dict.get('repos')
        if repo:
            self.section_dict['enabled_repos'] = repo
        if not repo and not action:
            print "Warning: Section 'yum' without any action option " \
                    "found. Skipping this section!"
            return
        if action:
            if action not in ['install', 'remove']:
                msg = "Unknown action provided. Use either `install` " \
                        "or `remove`."
                print "\nError: " + msg
                Global.logger.error(msg)
                return
            self.section_dict['yum_state'] = 'present' if action == 'install' else 'absent'
            self.check_for_param_presence('packages', self.section_dict)
            self.section_dict['name'] = self.section_dict.pop('packages')
        if not Global.hosts:
            print "Error: Hostnames not provided. Cannot continue!"
            self.cleanup_and_quit()
        self.section_dict = self.fix_format_of_values_in_config(self.section_dict)
        self.filename = Global.group_file
        self.iterate_dicts_and_yaml_write(self.section_dict)
        msg = "yum operation(action: %s) triggered" % action
        print "\nINFO: " + msg
        Global.logger.info(msg)
        Global.playbooks.append('yum-operation.yml')
