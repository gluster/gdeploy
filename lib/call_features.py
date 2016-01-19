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

import os
from helpers import Helpers
from global_vars import Global
import features

helpers = Helpers()

def call_features():
    return
    if not Global.sections:
        return
    map(get_feature_dir, Global.sections)



def get_feature_dir(section):
    global helpers
    section_dir = os.path.join(features.__path__[0], section)
    if not os.path.isdir(section_dir):
        return
    config_file = helpers.get_file_dir_path(section_dir, section + 'in')
    if not os.path.isfile(config_file):
        print "Error: Setup file not found for feature '%s'" % section
        return
    parse_the_user_config(section)


def parse_the_user_config(section):
    global helpers
    section_dict = Global.sections[section]
    section_dict = helpers.fix_format_of_values_in_config(section_dict)
    print section_dict
