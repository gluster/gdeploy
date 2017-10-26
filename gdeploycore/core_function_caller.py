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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

import re
import sys
import os
from gdeploylib import *
from gdeploylib.defaults import *
from backend_setup import BackendSetup
from backend_reset import BackendReset


yaml_write = YamlWriter()
conf_parse = Helpers()


def call_core_functions():
    BackendSetup()
    tune_profile()
    BackendReset()


def tune_profile():
    global conf_parse
    profile = conf_parse.config_get_options('tune-profile', False)
    profile = None if not profile else profile[0]
    if not profile:
        Global.logger.info("No tuning profiles specified, ignoring")
        return
    yaml_write.create_yaml_dict('profile', profile, False)
    Global.logger.info("Running tuneadm to apply profile %s" % profile)
    Global.logger.info("Executing playbook %s" % TUNE_YML)
    conf_parse.run_playbook(TUNE_YML)
    conf_parse.remove_from_sections('tune-profile')
