#!/usr/bin/python
# -*- coding: utf-8 -*-
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
#   gluster_deploy.py
#   ----------------
#
# gluster_deploy script, taking a configuration file as input,
# calls different methods in generator_module generating
# necessary ansible playbooks and variable files and then executes the
# playbooks using ansible-playbook command which sets up backend and then
# deploy gluster in all the hosts specified in the configuration file.
#

import argparse
import sys
import os
from generator_modules import ConfigParseHelpers
from generator_modules import VarFileGenerator


class GlusterDeploy(VarFileGenerator, ConfigParseHelpers):

    def __init__(self):
        args = self.parse_arguments()
        config_file = args.config_file.name
        self.base_dir = '/tmp/playbooks'
        VarFileGenerator(config_file, self.base_dir)
        self.deploy_gluster()
        self.cleanup(args.keep)

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

    def deploy_gluster(self):
        self.inventory = self.get_file_dir_path(self.base_dir,
                                                'ansible_hosts')
        if ConfigParseHelpers.setup_backend:
            self.set_up_yml = self.get_file_dir_path(self.base_dir,
                                                'setup-backend.yml')
            print "Setting up back-end..."
            self.call_ansible_command(self.set_up_yml)
        if ConfigParseHelpers.gluster_ret:
            self.gluster_deploy_yml = self.get_file_dir_path(self.base_dir,
                                            'gluster-deploy.yml')
            print "Deploying GlusterFS... Coming Soon!!!"
            #self.call_ansible_command(self.gluster_deploy_yml)

    def call_ansible_command(self, playbooks):
        try:
            cmd = 'ansible-playbook -i %s %s' % (
                self.inventory, playbooks)
            self.exec_cmds(cmd, '')
        except:
            print "Error: Looks like there is something wrong with " \
                "your ansible installation."


    def cleanup(self, keep):
        if not int(keep) and os.path.isdir(self.base_dir):
            self.exec_cmds('rm -rf', self.base_dir)
        else:
            print "You can view the generated configuration files "\
                "inside /tmp/playbooks/"

if __name__ == '__main__':
    GlusterDeploy()
