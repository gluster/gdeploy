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


class SubscriptionManagement(YamlWriter):

    def __init__(self, config):
        self.config = config
        try:
            self.section_dict = self.config._sections['RH-subscription']
            del self.section_dict['__name__']
        except KeyError:
            return
        self.get_subscription_data()


    def get_subscription_data(self):
        action = self.section_dict.get('action')
        if action:
            del self.section_dict['action']
        self.section_dict = self.fix_format_of_values_in_config(self.section_dict)
        if action == 'unregister':
            self.unregister()
        elif action == 'disable-repos':
            self.disable_repos()
        else:
            self.register_and_subscribe()
        if not Global.hosts:
            print "Error: Hostnames not provided. Cannot continue!"
            self.cleanup_and_quit()
        self.filename = Global.group_file
        print "\nINFO: Subscription management(action: %s) triggered" % action
        self.iterate_dicts_and_yaml_write(self.section_dict)

    def unregister(self):
        Global.playbooks.append('redhat_unregister.yml')

    def disable_repos(self):
        self.section_dict['repos'] = self.section_dict.get('repos') or '*'
        Global.playbooks.append('disable-repos.yml')


    def register_and_subscribe(self):
        self.section_dict['rhsm_repos'] = self.section_dict.get('repos') or []
        attach = self.section_dict.get('auto-attach')
        self.section_dict['attach'] = True if (
                attach and attach.lower() == 'true') else ''
        Global.playbooks.append('subscription_manager.yml')
