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
#    PlaybookGen, with the help of other helper methods from various
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
from yaml_writer import YamlWriter
from global_vars import Global
from gluster_conf_writer import GlusterConfWriter
from volume_management import VolumeManagement
from client_management import ClientManagement


class PlaybookGen(GlusterConfWriter):

    def __init__(self, config_file):
        self.config = self.read_config(config_file)
        self.options = self.config_get_sections(self.config)
        self.get_hostnames()
        self.create_files_and_dirs()
        self.get_var_file_type()
        Global.sections = self.config_get_sections(self.config)
        output = {'host_vars': self.host_vars_gen,
                  'group_vars': self.group_vars_gen
                  }[self.var_file]()
        '''
        since the client configuration data are to be written
        to the global_vars file no matter what, this method
        is called seperately
        '''
        VolumeManagement(self.config, self.var_file)
        ClientManagement(self.config)
        self.create_inventory()
        self.write_host_names(self.config, self.hosts)

    def get_hostnames(self):
        self.hosts = self.config_get_options(self.config, 'hosts', False)
        if not self.hosts:
            print "Error: Section `hosts' not found.\ngluster-deploy will "\
                "continue only if volume name is given in the format " \
                "<hostname>:<volumename>"

    def create_files_and_dirs(self):
        '''
        Creates required directories for all the configuration files
        to go in. Since the client data for gluster confs are common for all the
        hosts, creating a group var file anyway.
        '''
        self.mk_dir(Global.base_dir)
        self.mk_dir(Global.group_vars_dir)
        self.touch_file(Global.group_file)
        self.move_templates_to_playbooks()
        self.mk_dir(Global.host_vars_dir)

    def get_var_file_type(self):
        '''
        Decides if host_vars are to be created or everything can
        fit into the group_vars file based on the options provided
        in the configuration file. If all the hostnames are
        present as sections in the configuration file, assumes
        we need host_vars. Fails accordingly.
        '''
        if set(self.hosts).intersection(set(self.options)):
            if set(self.hosts).issubset(set(self.options)):
                self.var_file = 'host_vars'
            else:
                print "Error: Looks like you missed to give configurations " \
                    "for one or many host(s). Exiting!"
                self.cleanup_and_quit()
        else:
            self.var_file = 'group_vars'

    def create_inventory(self):
        self.hosts and self.write_config(
            Global.group,
            self.hosts,
            Global.inventory)
        if self.hosts or Global.master:
            self.write_config('master', Global.master or [self.hosts[0]],
                              Global.inventory)

    def host_vars_gen(self):
        '''
        If decided to create host, this will create host_vars file for
        each hosts and writes data to it, accorsing with the help of
        YAMLWriter
        '''
        for host in self.hosts:
            host_file = self.get_file_dir_path(Global.host_vars_dir, host)
            self.touch_file(host_file)
            devices = self.config_section_map(self.config, host,
                                              'devices', False)
            device_names = self.split_comma_seperated_options(devices)
            if device_names:
                YamlWriter(device_names, self.config, host_file,
                        self.var_file)

    def group_vars_gen(self):
        '''
        Calls YamlWriter for writing data to the group_vars file
        '''
        device_names = self.config_get_options(self.config,
                                               'devices', False)
        if device_names:
            YamlWriter(device_names, self.config, Global.group_file,
                    self.var_file)

    def template_files_create(self, temp_file):
        if not os.path.isdir(temp_file):
            return False
        self.exec_cmds('cp %s/*' % temp_file, Global.base_dir)
        return True

    def move_templates_to_playbooks(self):
        '''
        Templates directory in this codebase's repo will be moved to
        /tmp/playbooks
        '''
        # Is the templates present as a part of ansible installation?
        templates_path_pkg = '/usr/share/ansible/gdeploy/templates'
        # Or is it present in the source directory or installed via setuptools
        templates_path_bk = self.get_file_dir_path(self.uppath(__file__, 2),
                                                   'templates')
        templates_dir = [
            path for path in [
                templates_path_pkg,
                templates_path_bk] if os.path.isdir(path)]
        if not templates_dir:
            print "Error: Template files not found at %s or %s. " \
                "Check your ansible-gluster " \
                "installation and try " \
                "again." % (templates_path_pkg, templates_path_bk)
            self.cleanup_and_quit()
        self.template_files_create(templates_dir[0])


if __name__ == '__main__':
    # For playbook_gen to be standalone script.
    if len(sys.argv) < 2:
        print "Usage: var_populate configuration_file"
        sys.exit(0)
    PlaybookGen(sys.argv[1])
    print "You can find your configuration file inside " \
        "'%s' directory" % Global.base_dir
