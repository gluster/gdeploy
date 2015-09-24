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


class PeerManagement(YamlWriter):

    def __init__(self, config):
        self.config = config
        if self.config.has_section('peer'):
            action = self.config_section_map(self.config, 'peer', 'manage', False)
            if not action:
                print "Warning: Section 'peers' without any action option " \
                        "found. Skipping this section!"
                return
            Global.logger.info("Reading configuration in peer section")
            self.hosts = self.config_get_options(self.config, 'hosts', False)
            if not self.hosts:
                msg = "Although peer manage option is provided, " \
                        "no hosts are provided in the section. \n " \
                        "Skipping section `peer`"
                print "\nError: " + msg
                Global.logger.error(msg)
                return
            try:
                yml = {'probe': 'gluster-peer-probe.yml',
                       'detach': 'gluster-peer-detach.yml',
                       'ignore': None
                      }[action]
            except:
                mag = "Unknown action provided. Use either `probe` " \
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
                Global.playbooks.append('glusterd-start.yml')
            Global.playbooks.append(yml)
