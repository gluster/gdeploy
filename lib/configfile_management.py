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


class ConfigfileManagement(YamlWriter):

    def __init__(self, config):
        self.config = config
        self.filename = Global.group_file
        self.get_data()

    def get_data(self):
        try:
            self.section_dict = self.config._sections['update-file']
            del self.section_dict['__name__']
        except:
            return
        action = self.section_dict.get('action')
        if not action:
            print "\nWarning: No 'action' provided in 'update-file' " \
                    "section."
            return
        del self.section_dict['action']
        if action.lower() == 'copy':
            self.copy_file()
        elif action.lower() == 'edit':
            self.edit_file()
        elif action.lower() == 'add':
            self.add_file()
        else:
            print "\nError: Unknown 'action' in 'update-file'"
            return
        self.iterate_dicts_and_yaml_write(self.section_dict)

    def copy_file(self):
        self.section_dict = self.format_values(self.section_dict)
        self.is_option_present('src', self.section_dict)
        self.is_option_present('dest', self.section_dict)
        src = self.pattern_stripping(self.section_dict['src'])
        dest = self.pattern_stripping(self.section_dict['dest'])
        if len(dest) == 1:
            dest *= len(src)
        if len(dest) != len(src):
            print "\nError: Provide same number of 'src' and 'dest' or " \
                    "provide a common 'dest'"
            return
        data = []
        for sr, de in zip(src, dest):
            files_list = {}
            files_list['src'] = sr
            files_list['dest'] = de
            data.append(files_list)
        self.create_yaml_dict('file_paths', data, True)
        Global.playbooks.append('move-file-from-local-to-remote.yml')

    def edit_file(self):
        self.section_dict = self.format_values(self.section_dict)
        self.is_option_present('dest', self.section_dict)
        self.is_option_present('line', self.section_dict)
        self.is_option_present('replace', self.section_dict)
        line = self.pattern_stripping(self.section_dict['line'])
        dest = self.pattern_stripping(self.section_dict['dest'])
        replace = self.pattern_stripping(self.section_dict['replace'])
        data = []
        if len(replace) != len(line):
            print "\nError: Provide same number of 'replace' and 'line'"
            return
        for li, re in zip(line, replace):
            files_list = {}
            files_list['line'] = li
            files_list['replace'] = re
            data.append(files_list)
        self.create_yaml_dict('file_paths', data, True)
        Global.playbooks.append('edit-remote-file.yml')

    def add_file(self):
        self.section_dict = self.format_values(self.section_dict)
        self.is_option_present('dest', self.section_dict)
        self.is_option_present('line', self.section_dict)
        self.section_dict['line'] = self.pattern_stripping(
                self.section_dict['line'])
        Global.playbooks.append('add-remote-file.yml')
