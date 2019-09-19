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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

from gdeploylib import *
from gdeploylib.defaults import *
import re


class BackendReset(Helpers):

    def __init__(self):
        self.get_breset_data()
        self.remove_from_sections('backend-reset')

    def get_breset_data(self):
        section_regexp = '^backend-reset(:)*(.*)'
        hosts = []
        backend_reset = False
        for section in Global.sections:
            val = re.search(section_regexp, section)
            if val:
                backend_reset = True
                if val.group(2):
                    hosts.append(val.group(2))
        if not backend_reset:
            return
        hosts = list(filter(None, hosts))
        ret = self.parse_section('')
        if hosts:
            hosts = self.pattern_stripping(hosts)
            for host in hosts:
                Global.current_hosts = [host]
                self.host_file = self.get_file_dir_path(Global.host_vars_dir,
                                                        host)
                self.touch_file(self.host_file)
                ret = self.parse_section(':' + host)


    def parse_section(self, hostname):
        try:
            self.section_dict = Global.sections['backend-reset' +
                    hostname]
            del self.section_dict['__name__']
        except KeyError:
            return
        self.get_backend_data()
        try:
            self.filename = self.host_file
        except:
            self.filename =  Global.group_file
            Global.current_hosts = Global.hosts
        Global.logger.info("Resetting disks on %s"%Global.hosts)
        self.run_playbook(BRESET_YML)
        return True

    def get_backend_data(self):
        self.section_dict = self.format_values(self.section_dict)
        self.set_default_values(self.section_dict, BRESET_DEFAULTS)
        for key, value in self.section_dict.items():
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
