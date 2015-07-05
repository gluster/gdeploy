#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import ConfigParser
import sys


class ConfigParseHelpers(object):

    def call_config_parser(self):
        config = ConfigParser.ConfigParser(allow_no_value=True)
        config.optionxform = str
        return config

    def read_config(self, config_file):
        config_parse = self.call_config_parser()
        try:
            config_parse.read(config_file)
            return config_parse
        except AttributeError as msg:
            print "Sorry! Looks like the format of configuration " \
                "file is not something we could read! \nTry removing " \
                "whitespaces or unwanted characters in the configuration " \
                "file."
            sys.exit(0)

    def write_config(self, section, options, filename):
        config = self.call_config_parser()
        config.add_section(section)
        for option in options:
            config.set(section, option)
        try:
            with open(filename, 'wb') as file:
                config.write(file)
        except:
            print "Error: Failed to create file %s. Exiting!" % filename
            sys.exit(0)

    def config_section_map(self, config_parse, section, option, required):
        try:
            return config_parse.get(section, option)
        except:
            if required:
                print "Error: Option %s not found! Exiting!" % option
                sys.exit(0)
            return []

    def config_get_options(self, config_parse, section, required):
        try:
            return config_parse.options(section)
        except ConfigParser.NoSectionError as e:
            if required:
                print "Error: Section %s not found in the " \
                    "configuration file" % section
                sys.exit(0)
            return []

    def config_get_sections(self, config_parse):
        try:
            return config_parse.sections()
        except:
            print "Error: Looks like you haven't provided any options " \
                "I need in the conf " \
                "file. Please populate the conf file and retry!"
            sys.exit(0)
