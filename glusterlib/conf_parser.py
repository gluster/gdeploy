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
#
#
#   conf_parser.py
#   -------------
#    ConfigParseHelpers use the ConfigParser python module to read
#    the configuration file specified by the user while calling the
#    gluster_deploy script. The mehtods in this class are called from
#    various parts of the framework to manipulate (both read and write)
#    the configuration files.
#

import argparse
import ConfigParser
import sys
from helpers import Helpers


class ConfigParseHelpers(Helpers):

    def call_config_parser(self):
        config = ConfigParser.ConfigParser(allow_no_value=True)
        config.optionxform = str
        return config

    def read_config(self, config_file):
        config_parse = self.call_config_parser()
        try:
            config_parse.read(config_file)
            return config_parse
        except:
            print "Sorry! Looks like the format of configuration " \
                "file is not something we could read! \nTry removing " \
                "whitespaces or unwanted characters in the configuration " \
                "file."
            self.cleanup_and_quit()

    def write_config(self, section, options, filename):
        config = self.call_config_parser()
        config.add_section(section)
        for option in options:
            config.set(section, option)
        try:
            with open(filename, 'ab') as file:
                config.write(file)
        except:
            print "Error: Failed to create file %s. Exiting!" % filename
            self.cleanup_and_quit()

    def config_section_map(
            self,
            config_parse,
            section,
            option,
            required=False):
        try:
            return config_parse.get(section, option)
        except:
            if required:
                print "Error: Option %s not found! Exiting!" % option
                self.cleanup_and_quit()
            return []

    def get_option_dict(self, config_parse, section, required=False):
        try:
            return config_parse.items(section)
        except:
            if required:
                print "Error: Section %s not found in the " \
                    "configuration file" % section
                self.cleanup_and_quit()
            return []

    def config_get_options(self, config_parse, section, required):
        try:
            return config_parse.options(section)
        except ConfigParser.NoSectionError as e:
            if required:
                print "Error: Section %s not found in the " \
                    "configuration file" % section
                self.cleanup_and_quit()
            return []

    def config_get_sections(self, config_parse):
        try:
            return config_parse.sections()
        except:
            print "Error: Looks like you haven't provided any options " \
                "I need in the conf " \
                "file. Please populate the conf file and retry!"
            self.cleanup_and_quit()
