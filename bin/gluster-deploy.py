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

import argparse
import sys
import os
from glusterlib import Global
from glusterlib import PlaybookGen
from glusterlib import CliOps
from collections import OrderedDict


class GlusterDeploy(PlaybookGen, Global):

    '''
    This class makes use of the class PlaybookGen inside glusterlib
    library to create the ansible playbooks and variable files.
    Then calls ansible-playbook command to setup back-end and
    deploy GlusterFS
    '''

    def __init__(self):
        args = self.parse_arguments()
        if args.config_file:
            config_file = args.config_file.name
            PlaybookGen(config_file)
            self.deploy_gluster()
        if args.volumeset:
            CliOps(args.volumeset)
            self.deploy_gluster()
        if not args.keep:
            self.cleanup_and_quit()
        else:
            print "You can view the generated configuration files "\
                "inside /tmp/playbooks/"

    def parse_arguments(self):
        '''
        This method uses argparser to parse the command line inputs
        to the gluster-deploy script
        '''
        usage = 'gluster-deploy.py [-h] [-v] [-c CONFIG_FILE] ' \
            '[-k] [volumeset <hostIP>:<volumename> <key> <value>]'
        parser = argparse.ArgumentParser(usage=usage, version='1.0')
        parser.add_argument('-c', dest='config_file',
                            help="Configuration file",
                            type=argparse.FileType('rt'))
        parser.add_argument('volumeset',
                            help="Set options for the volume",
                            nargs='*')
        parser.add_argument('-k', dest='keep',
                            action='store_true',
                            help="Keep the generated ansible utility files")
        try:
            args = parser.parse_args()
        except IOError as msg:
            parser.error(str(msg))
        both_not_present =  not (args.config_file or args.volumeset)
        if both_not_present:
            parser.print_help()
            self.cleanup_and_quit()
        return args

    def deploy_gluster(self):
        '''
        Checks if the necessary variables for backend-setup and
        gluster deploy are populated.
        '''
        if Global.volume_set:
            the_playbook = self.get_file_dir_path(Global.base_dir,
                    'gluster-volume-set.yml')
            self.call_ansible_command(the_playbook)
            return
        elif Global.shell_cmd:
            the_playbook = self.get_file_dir_path(Global.base_dir,
                    'shell_cmd.yml')
            self.call_ansible_command(the_playbook)
            return

        playbooks = ' '
        basic_operations = OrderedDict([
                            ('setup-backend.yml', Global.do_setup_backend),
                            ('probe_and_create_volume.yml',
                                                 Global.do_volume_create),
                            ('gluster-client-mount.yml',
                                                 Global.do_volume_mount),
                            ('gluster-volume-delete.yml',
                                                Global.do_volume_delete),
                            ('client_volume_umount.yml',
                                                 Global.do_volume_umount),
                            ])
        for yml, op in basic_operations.iteritems():
            if op:
                playbooks += ' ' + self.get_file_dir_path(Global.base_dir, yml)

        self.call_ansible_command(playbooks)
        #Each additional feature like snapshot, NFS-Ganesha is to be added
        #here
        features = OrderedDict([
                   ('snapshot-setup.yml', Global.create_snapshot),
                   ('gluster-snapshot-delete.yml', Global.delete_snapshot),
                   ('ganesha-setup.yml', Global.setup_ganesha)
                   ])

        for yml, feature in features.iteritems():
            if feature:
                the_playbook = self.get_file_dir_path(Global.base_dir, yml)
                self.call_ansible_command(the_playbook)

    def call_ansible_command(self, playbooks):
        '''
        Calls the ansible-playbook command on necessary yamls
        '''
        if playbooks.strip():
            try:
                cmd = 'ansible-playbook -i %s %s' % (
                    Global.inventory, playbooks)
                self.exec_cmds(cmd, '')
            except:
                print "Error: Looks like there is something wrong with " \
                    "your ansible installation."


if __name__ == '__main__':
    GlusterDeploy()
