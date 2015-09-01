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


class GeorepManagement(YamlWriter):

    def __init__(self, config):
        self.config = config
        self.filename = Global.group_file
        self.get_georep_data()


    def get_georep_data(self):
        try:
            self.section_dict = self.config._sections['geo-replication']
            del self.section_dict['__name__']
        except KeyError:
            return
        #self.action = self.section_dict.get('action')
        #if not self.action:
            #print "\nWarning: Section 'geo-replication' without any action "\
                    #"option found. Skipping this section!"
            #return
        #del self.section_dict['action']
        self.parse_georep_section()


    def parse_georep_section(self):
        self.check_for_param_presence('mastervol', self.section_dict, True)
        self.check_for_param_presence('slavevol', self.section_dict, True)
        master, mastervolname = self.split_val_and_hostname(self.section_dict(
            'mastervol'), True)
        slave, slavevolname = self.split_val_and_hostname(self.section_dict(
            'slavevol'), True)
        self.write_config('georep_master', [master[0]], Global.inventory)
        self.write_config('georep_slave', [slave[0]], Global.inventory)
        self.section_dict['mastervolname'] = mastervolname
        self.section_dict['slavevolname'] = slavevolname

