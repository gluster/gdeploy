#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Nandaja Varma <nvarma@redhat.com>
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
import re, sys, os
from lib import *
from lib.defaults import *
from backend_setup import BackendSetup
from peer_management import PeerManagement
from volume_management import VolumeManagement
from client_management import ClientManagement
from backend_reset import BackendReset


yaml_write = YamlWriter()
conf_parse = ConfigParseHelpers()


@logfunction
def call_core_functions():
    log_methods_in_class(BackendSetup)
    tune_profile()
    log_methods_in_class(PeerManagement)
    log_methods_in_class(VolumeManagement)
    log_methods_in_class(ClientManagement)
    log_methods_in_class(BackendReset)

def log_methods_in_class(classname):
    obj = logclass(classname)
    obj()

@logfunction
def tune_profile():
    profile = conf_parse.config_get_options('tune-profile', False)
    profile = None if not profile else profile[0]
    if not profile:
        return
    yaml_write.create_yaml_dict('profile', profile, False)
    self.run_playbook(TUNE_YML)
    remove_entry_from_sections('tune-profile')


