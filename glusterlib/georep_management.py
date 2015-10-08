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

from yaml_writer import YamlWriter
from conf_parser import ConfigParseHelpers
from global_vars import Global
from helpers import Helpers


class GeorepManagement(YamlWriter):

    def __init__(self, config):
        self.config = config
        self.filename = Global.group_file
        self.get_georep_data()


    def get_georep_data(self):
        try:
            self.section_dict = self.config._sections['geo-replication']
            del self.section_dict['__name__']
        except KeyError:
            return
        action = self.section_dict.get('action')
        if not action:
            print "\nWarning: Section 'geo-replication' without any action "\
                    "option found. Skipping this section!"
            return
        del self.section_dict['action']
        sections_default_value = {
                'secure': 'no',
                'user': 'root' }
        self.set_default_value_for_dict_key(self.section_dict,
                                            sections_default_value)
        self.section_dict = self.fix_format_of_values_in_config(self.section_dict)
        self.parse_georep_section()
        action_func =  { 'create': self.create_session,
                          'start': self.start_session,
                          'stop': self.stop_session,
                          'delete': self.delete_session,
                          'pause': self.pause_session,
                          'resume': self.resume_session,
                          'config': self.config_session,
                          'secure-session': self.secure_session
                        }.get(action)
        if not action_func:
            msg = "Unknown action provided for volume. \nSupported " \
                    "actions are:\n " \
                    "create, delete, start, stop, add-brick, remove-brick, " \
                    "and rebalance"
            print "\nError: " + msg
            Global.logger.error(msg)
            return
        action_func()
        msg = "Geo-replication management (action: %s) triggered" % action
        Global.logger.info(msg)
        print "\nINFO: " + msg
        force = self.section_dict.get('force')
        self.section_dict['force'] = 'yes' if force == 'yes' else 'no'
        self.iterate_dicts_and_yaml_write(self.section_dict)


    def parse_georep_section(self):
        self.check_for_param_presence('mastervol', self.section_dict, True)
        self.check_for_param_presence('slavevol', self.section_dict, True)
        master, mastervolname = self.split_georep_volname(self.section_dict.get(
            'mastervol'))
        slave, slavevolname = self.split_georep_volname(self.section_dict.get(
            'slavevol'))
        self.write_config('georep_master', [master[0]], Global.inventory)
        self.write_config('georep_slave', [slave[0]], Global.inventory)
        self.write_config('georep_slaves', slave, Global.inventory)
        self.section_dict['mastervolname'] = mastervolname
        self.section_dict['slavevolname'] = slavevolname

    def create_session(self):
        Global.logger.info("Setting up passwordless ssh between master and slave")
        Global.playbooks.append('georep_common_public_key.yml')
        Global.playbooks.append('georep-session-create.yml')

    def start_session(self):
        Global.playbooks.append('georep-session-start.yml')

    def stop_session(self):
        Global.playbooks.append('georep-session-stop.yml')

    def delete_session(self):
        Global.playbooks.append('georep-session-stop.yml')
        Global.playbooks.append('georep-session-delete.yml')

    def pause_session(self):
        Global.playbooks.append('georep-session-pause.yml')

    def resume_session(self):
        Global.playbooks.append('georep-session-resume.yml')

    def config_session(self):
        sections_default_value = {
            'gluster-log-file' : None,
            'gluster-log-level' : None,
            'log-file' : None,
            'log-level' : None,
            'ssh-command' : None,
            'rsync-command' : None,
            'use-tarssh' : None,
            'volume-id' : None,
            'timeout' : None,
            'sync-jobs' : None,
            'ignore-deletes' : None,
            'checkpoint' : None}
        self.set_default_value_for_dict_key(self.section_dict,
                                            sections_default_value)
        config_options = sections_default_value.keys()
        for key in config_options:
            if '-' in key:
                new_key = key.replace('-', '_')
                self.section_dict[new_key] = self.section_dict.get(key)
                del self.section_dict[key]

        Global.playbooks.append('georep-session-config.yml')


    def secure_session(self):
        self.section_dict['secure'] = 'yes'
        self.section_dict['user'] = 'geoaccount'
        Global.logger.info("Setting up passwordless ssh between master and slave")
        Global.playbooks.append('georep-secure-session.yml')
        Global.playbooks.append('georep_common_public_key.yml')
        Global.playbooks.append('georep-session-create.yml')
        Global.playbooks.append('georep-set-pemkeys.yml')
        Global.playbooks.append('georep-session-start.yml')
