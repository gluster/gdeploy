#!/usr/bin/python
# -*- coding: utf-8 -*-
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
import argparse
import sys
from generator_modules import ConfigParseHelpers
from generator_modules import VarFileGenerator


class GlusterDeploy(VarFileGenerator, ConfigParseHelpers):

    def __init__(self):
        args = self.parse_arguments()
        config_file = args.config_file.name
        self.config = self.read_config(config_file)
        self.base_dir = '/tmp/playbooks'
        self.set_up_yml = self.get_file_dir_path(self.base_dir,
                                            'setup-backend.yml')
        self.group = 'rhs_servers'
        self.inventory = self.get_file_dir_path(self.base_dir,
                                                'ansible_hosts')
        self.var_file_type_check()
        self.write_config(self.group, self.hosts, self.inventory)
        self.deploy_gluster()
        if not args.keep:
            self.exec_cmds('rm -rf', self.base_dir)
        else:
            print "You can view the generated configuration files "\
                "inside /tmp/playbooks/"

    def parse_arguments(self):
        parser = argparse.ArgumentParser(version='1.0')
        parser.add_argument('-c', dest='config_file',
                            help="Configuration file",
                            type=argparse.FileType('rt'),
                            required=True)
        parser.add_argument('-k', dest='keep', const='1',
                            default='0',
                            action='store',
                            nargs='?',
                            help="Keep the generated ansible utility files")
        try:
            return parser.parse_args()
        except IOError as msg:
            parser.error(str(msg))

    def var_file_type_check(self):
        options = self.config_get_sections(self.config)
        self.hosts = self.config_get_options(self.config, 'hosts', True)
        if set(self.hosts).intersection(set(options)):
            if set(self.hosts).issubset(set(options)):
                var_type = 'host_vars'
            else:
                print "Error: Looks like you missed to give configurations " \
                    "for one or many host(s). Exiting!"
                sys.exit(0)
        else:
            var_type = 'group_vars'
        VarFileGenerator(var_type, options, self.hosts, self.config,
                         self.base_dir, self.group)

    def deploy_gluster(self):
        try:
            cmd = 'ansible-playbook -i %s %s' % (
                self.inventory, self.set_up_yml)
            self.exec_cmds(cmd, '')
        except:
            print "Error: Looks like there is something wrong with " \
                "your ansible installation."

if __name__ == '__main__':
    GlusterDeploy()
