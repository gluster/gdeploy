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
#    This script can be called separately even, providing the configuration
#    file and the directory to which the ansible playbooks and variable files
#    are to be generated(this is optional.Default is '/var/tmp/playbooks'
#    Usage: ./playbook_gen.py <configuration_file> [<directory name>]
#

import os
import sys
from global_vars import Global
from backend_setup import BackendSetup
from volume_management import VolumeManagement
from client_management import ClientManagement
from peer_management import PeerManagement
from snapshot_management import SnapshotManagement
from ganesha_management import GaneshaManagement
from quota_management import QuotaManagement
from georep_management import GeorepManagement
from gdeploy_logging import log_event
from subscription_management import SubscriptionManagement
from firewalld_management import FirewalldManagement
from backend_reset import BackendReset
from package_management import PackageManagement
from ctdb_management import CtdbManagement
from configfile_management import ConfigfileManagement



class PlaybookGen(BackendSetup):

    def __init__(self, config_file):
        self.config = self.read_config(config_file)
        self.options = self.config_get_sections(self.config)
        Global.sections = self.config._sections
        self.get_hostnames()
        self.create_files_and_dirs()
        self.get_backend_sections()
        BackendSetup(self.config)
        for warn in Global.warnings:
            print warn
        self.tune_profile()
        SubscriptionManagement(self.config)
        PackageManagement(self.config)
        FirewalldManagement(self.config)
        PeerManagement(self.config)
        ConfigfileManagement(self.config)
        VolumeManagement(self.config)
        CtdbManagement(self.config)
        SnapshotManagement(self.config)
        GaneshaManagement(self.config)
        ClientManagement(self.config)
        QuotaManagement(self.config)
        GeorepManagement(self.config)
        BackendReset(self.config)
        self.create_inventory()
        self.write_host_names()

    def get_hostnames(self):
        hosts = self.config_get_options(self.config, 'hosts', False)
        for host in hosts:
            Global.hosts += self.parse_patterns(host)

    def create_files_and_dirs(self):
        '''
        Creates required directories for all the configuration files
        to go in. Since the client data for gluster confs are common for all the
        hosts, creating a group var file anyway.
        '''
        Global.logger.info("Creating necessary files and folders")
        self.mk_dir(Global.group_vars_dir)
        self.touch_file(Global.group_file)
        self.touch_file(Global.inventory)
        self.move_templates_to_playbooks()
        self.mk_dir(Global.host_vars_dir)

    def create_inventory(self):
        Global.hosts and self.write_config(
            Global.group,
            Global.hosts,
            Global.inventory)
        if not Global.master or Global.master in Global.brick_hosts:
            try:
                Global.master = [list(set(Global.hosts) - set(
                    Global.brick_hosts))[0]]
            except:
                Global.master = None
        if Global.hosts or Global.master:
            self.write_config('master', Global.master or [Global.hosts[0]],
                              Global.inventory)

    def write_host_names(self):
        self.filename = Global.group_file
        to_be_probed = Global.hosts + Global.brick_hosts
        self.create_yaml_dict('hosts', Global.hosts, False)
        self.create_yaml_dict('to_be_probed', to_be_probed, False)

    def tune_profile(self):
        self.filename = Global.group_file
        profile = self.config_get_options(self.config,
                               'tune-profile', False)
        profile = None if not profile else profile[0]
        if not profile:
            return
        self.create_yaml_dict('profile', profile, False)
        if 'tune-profile.yml' not in Global.playbooks:
            Global.playbooks.append('tune-profile.yml')


    def template_files_create(self, temp_file):
        if not os.path.isdir(temp_file):
            return False
        templates = self.copy_files(temp_file)
        return True

    def move_templates_to_playbooks(self):
        '''
        Templates directory in this codebase's repo will be moved to
        /var/tmp/playbooks
        '''
        templates_path_pkg = '/usr/share/ansible/gdeploy/templates'
        templates_env_var = os.getenv('GDEPLOY_TEMPLATES')
        # Is environment variable GDEPLOY_TEMPLATES set
        if templates_env_var:
            templates_dir = self.get_file_dir_path(templates_env_var,
                    'templates')
        # Or assumes the templates are present as a part of ansible installation
        else:
            templates_dir = templates_path_pkg
        if not os.path.isdir(templates_dir):
            msg = "Template files not found.\n\n" \
                "Gdeploy looks inside the directory %s or \n" \
                "wants the environment varible GDEPLOY_TEMPLATES set."\
                 % (templates_path_pkg)
            print "\nError: " + msg
            Global.logger.error(msg)
            self.cleanup_and_quit()
        self.template_files_create(templates_dir)


if __name__ == '__main__':
    # For playbook_gen to be standalone script.
    log_event()
    if len(sys.argv) < 2:
        print "Usage: var_populate configuration_file"
        sys.exit(0)
    PlaybookGen(sys.argv[1])
    print "You can find your configuration file inside " \
        "'%s' directory" % Global.base_dir
