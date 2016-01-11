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

from lib import *
import re


class BackendReset(YamlWriter):

    def __init__(self, section):
        return
        self.config = config
        section_regexp = '^backend-reset(:)*(.*)'
        sections = self.config._sections
        hosts = []
        backend_reset = False
        for section in sections:
            val = re.search(section_regexp, section)
            if val:
                backend_reset = True
                if val.group(2):
                    hosts.append(val.group(2))
        if not backend_reset:
            return
        hosts = filter(None, hosts)
        ret = self.parse_section('')
        if hosts:
            hosts = self.pattern_stripping(hosts)
            Global.hosts.extend(hosts)
            for host in hosts:
                self.host_file = self.get_file_dir_path(Global.host_vars_dir, host)
                self.touch_file(self.host_file)
                ret = self.parse_section(':' + host)

        if not Global.hosts:
            print "Error: Hostnames not provided. Cannot continue!"
            self.cleanup_and_quit()
        if ret:
            print "\nINFO: Back-end reset triggered"

    def parse_section(self, hostname):
        try:
            self.section_dict = Global.dictionary['backend-reset' +
                    hostname]
            del self.section_dict['__name__']
        except KeyError:
            return
        self.get_backend_data()
        try:
            self.filename = self.host_file
        except:
            self.filename =  Global.group_file
        self.iterate_dicts_and_yaml_write(self.section_dict)
        if 'backend-reset.yml' not in Global.playbooks:
            Global.playbooks.append('backend-reset.yml')
        return True

    def get_backend_data(self):
        self.section_dict = self.fix_format_of_values_in_config(self.section_dict)
        sections_default_value = {
                'pvs': None,
                'vgs': None,
                'lvs': None,
                'mountpoints': None,
                'unmount': "no" }
        self.set_default_value_for_dict_key(self.section_dict,
                                            sections_default_value)
        for key, value in self.section_dict.iteritems():
            if value:
                self.section_dict[key] = self.pattern_stripping(value)
        pvs = self.section_dict.get('pvs')
        if pvs:
            bricks = []
            for pv in pvs:
                if not pv.startswith('/dev/'):
                    bricks.append('/dev/' + pv)
                else:
                    bricks.append(pv)
            self.section_dict['pvs'] = bricks
