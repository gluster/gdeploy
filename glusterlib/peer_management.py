#!/usr/bin/python # -*- coding: utf-8 -*-
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


class PeerManagement(YamlWriter):

    def __init__(self, config):
        self.config = config
        if self.config.has_section('peer'):
            action = self.config_section_map(self.config, 'peer', 'manage', True)
            self.hosts = self.config_get_options(self.config, 'hosts', False)
            if not self.hosts:
                print "Error: Although peer manage option is provided, " \
                        "no hosts are provided in the section. " \
                        "Skipping section `peer`"
                return
            try:
                yml = {'probe': 'gluster-peer-probe.yml',
                       'detach': 'gluster-peer-detach.yml'
                      }[action]
            except:
                print "Error: Unknown action provided. Use either `probe` " \
                        "or `detach`."
                return
            print "INFO: Peer management triggered"
            Global.playbooks.append('glusterd-start.yml')
            Global.playbooks.append(yml)
