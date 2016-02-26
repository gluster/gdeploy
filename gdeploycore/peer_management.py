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

from gdeploylib import *
from gdeploylib.defaults import *


class PeerManagement(Helpers):

    def __init__(self):
        Global.current_hosts = Global.hosts
        self.get_peer_data()
        self.remove_from_sections('peer')


    def get_peer_data(self):
        if Global.sections.get('peer'):
            action = self.config_section_map('peer', 'manage', False)
            if action:
                print "Warning: The option 'manage' is deprecated. " \
                "Please use 'action' instead."
            else:
                action = self.config_section_map('peer', 'action', False)
            if not action:
                return
            Global.logger.info("Reading configuration in peer section")
            if not Global.hosts:
                msg = "Although peer manage option is provided, " \
                        "no hosts are provided in the section. \n " \
                        "Skipping section `peer`"
                print "\nError: " + msg
                Global.logger.error(msg)
                return
            try:
                yml = {'probe': PROBE_YML,
                       'detach': DETACH_YML,
                       'ignore': None
                      }[action]
            except:
                msg = "Unknown action provided. Use either `probe` " \
                        "or `detach`."
                print "\nError: " + msg
                Global.logger.error(msg)
                return
            if not yml:
                return
            msg = "Peer management(action: %s) triggered" % action
            print "\nINFO: " + msg
            Global.logger.info(msg)
            if action == 'probe':
                self.run_playbook(GLUSTERD_YML)
            if action == 'probe':
                to_be_probed = Global.hosts + Global.brick_hosts
                self.create_yaml_dict('to_be_probed', to_be_probed, False)
            elif action == 'detach':
                self.create_yaml_dict('hosts', Global.hosts, False)
            self.run_playbook(yml)
