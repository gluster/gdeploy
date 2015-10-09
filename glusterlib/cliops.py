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

from yaml_writer import YamlWriter
from conf_parser import ConfigParseHelpers
from global_vars import Global
from playbook_gen import PlaybookGen
import re
from helpers import Helpers


class CliOps(PlaybookGen):

    def __init__(self, volumeset):

        if volumeset[0] == 'volumeset':
            # for volumeset option (gluster volume set)
            try:
                cmd, volume, key, value = volumeset
            except:
                print "Error: Insufficient number of arguments for volumeset"
                self.cleanup_and_quit()
            vol_group = re.match("(.*):(.*)", volume)
            if not vol_group:
                print "Error: Provide volume name in the format " \
                    "<hostname>:<volume name>"
                self.cleanup_and_quit()
            host_ip = [vol_group.group(1)]
            volname = vol_group.group(2)
            self.create_files_and_dirs()
            self.write_config('master', host_ip, Global.inventory)
            variables = {'key': key,
                         'value': value,
                         'volname': volname
                         }
            Global.playbooks.append('gluster-volume-set.yml')
            self.filename = Global.group_file
            self.write_yaml(variables, False)
        else:
            print "Error: Invalid Argument. Use gdeploy -h for the help message"
            self.cleanup_and_quit()
