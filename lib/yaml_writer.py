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
#
#
#    yaml_writer.py
#    -------------
#    YamlWriter is a helper class used by VarFileGenerator to write
#    all the necessary sections and options into the yaml file
#    as per specified in the configuration file
#

from conf_parser import ConfigParseHelpers
from global_vars import Global
from helpers import Helpers
try:
    import yaml
except ImportError:
    msg = "Package PyYAML not found."
    print "\nError: " + msg
    Global.logger.error(msg)
    sys.exit(0)
import os


class YamlWriter(ConfigParseHelpers):

    def iterate_dicts_and_yaml_write(self, data_dict, keep_format=False):
        # Just a pretty wrapper over create_yaml_dict to iterate over dicts
        for key, value in data_dict.iteritems():
            if key not in ['__name__']:
                self.create_yaml_dict(key, value, keep_format)

    def create_yaml_dict(self, section, data, keep_format=True):
        '''
        This method is called if in the playbook yaml,
        the options are to be written as a list
        '''
        data_dict = {}
        data_dict[section] = data
        self.write_yaml(data_dict, keep_format)

    def write_yaml(self, data_dict, data_flow):
        list_doc = {}
        if not hasattr(self, 'filename'):
            self.filename = Global.group_file
        with open(self.filename) as f:
            list_doc = yaml.load(f) or {}
        list_doc.update(data_dict)
        with open(self.filename, 'w') as outfile:
            if not data_flow:
                outfile.write(
                    yaml.dump(
                        list_doc,
                        default_flow_style=data_flow))
            else:
                outfile.write(yaml.dump(list_doc))
