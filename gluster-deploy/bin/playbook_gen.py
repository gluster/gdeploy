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
#    playbook_gen.py
#    ----------------------
#    VarFileGenerator, with the help of other helper methods from various
#    classes in the package, creates the variable files for the ansible
#    playbooks to read from.
#
#    This script can be called seperately even, providing the configuration
#    file and the directory to which the ansible playbooks and variable files
#    are to be generated(this is optional.Default is '/tmp/playbooks'
#    Usage: ./playbook_gen.py <configuration_file> [<directory name>]
#

import os
import sys
from lib import YamlWriter
from lib import Global


class PlaybookGen(YamlWriter):

    def __init__(self, config_file):
        self.config = self.read_config(config_file)
        options = self.config_get_sections(self.config)
        self.hosts = self.config_get_options(self.config, 'hosts', True)
        if set(self.hosts).intersection(set(options)):
            if set(self.hosts).issubset(set(options)):
                self.var_file = 'host_vars'
            else:
                print "Error: Looks like you missed to give configurations " \
                    "for one or many host(s). Exiting!"
                self.cleanup_and_quit()
        else:
            self.var_file = 'group_vars'
        vars_dir = self.get_file_dir_path(Global.base_dir, self.var_file)
        dir_list = [Global.base_dir, vars_dir]
        self.mk_dir(dir_list)
        output = {'host_vars': self.host_vars_gen,
                  'group_vars': self.group_vars_gen
                  }[self.var_file](vars_dir)
        self.move_templates_to_playbooks()
        self.create_inventory()

    def create_inventory(self):
        self.write_config(Global.group, self.hosts, Global.inventory)

    def host_vars_gen(self, host_vars_path):
        for host in self.hosts:
            host_file = self.get_file_dir_path(host_vars_path, host)
            self.touch_file(host_file)
            device_names = filter(
                None,
                self.config_section_map(
                    self.config,
                    host,
                    'devices',
                    True).split(','))
            YamlWriter(device_names, self.config, host_file, self.var_file)

    def group_vars_gen(self, group_vars_path):
        group_file = self.get_file_dir_path(group_vars_path, Global.group)
        self.touch_file(group_file)
        device_names = self.config_get_options(self.config,
                                               'devices', False)
        YamlWriter(device_names, self.config, group_file, self.var_file)

    def template_files_create(self, temp_file):
        if not os.path.isdir(temp_file):
            return False
        self.exec_cmds('cp %s/*' % temp_file, Global.base_dir)
        return True

    def move_templates_to_playbooks(self):
        templates_path = '/usr/share/ansible/ansible-glusterfs/templates'
        templates_path_bk = self.get_file_dir_path(os.path.dirname(__file__),
                '../templates')
        if not (self.template_files_create(templates_path) or
                self.template_files_create(templates_path_bk)):
            print "Error: Template files not found at %s or %s. " \
                "Check your ansible-gluster " \
                "installation and try " \
                "again." % (templates_path, templates_path_bk)
            self.cleanup_and_quit()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: var_populate configuration_file"
        sys.exit(0)
    PlaybookGen(sys.argv[1])
    print "You can find your configuration file inside " \
            "'%s' directory" % Global.base_dir



