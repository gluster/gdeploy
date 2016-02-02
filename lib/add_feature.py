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

from lib import *
import os, json


def add_feature(feature):
    feature = feature.lower().replace('-', '_')
    helpers = Helpers()
    base_dir = helpers.get_file_dir_path(helpers.uppath(os.getcwd(), 0), 'features')
    feature_dir = helpers.get_file_dir_path(helpers.uppath(
        os.getcwd(), 1), 'gdeploy/features/%s' % feature)
    JSON_FILE = helpers.get_file_dir_path(feature_dir, '%s.json' % feature)
    PYTHON_SCRIPT = helpers.get_file_dir_path(feature_dir, '%s.py' % feature)
    INIT_FILE = helpers.get_file_dir_path(feature_dir, '__init__.py')
    BASE_INIT_FILE = helpers.get_file_dir_path(base_dir, '__init__.py')

    helpers.mk_dir(feature_dir)
    helpers.touch_file(JSON_FILE)
    helpers.touch_file(PYTHON_SCRIPT)
    helpers.touch_file(INIT_FILE)


    init_file_line = "import %s\n" % feature
    print init_file_line

    with open(INIT_FILE, 'a') as f:
        f.write(init_file_line)


    with open(BASE_INIT_FILE, 'a') as f:
        f.write(init_file_line)

    data = { feature:
                { "action":
                    { "action1":
                        { "options": [
                                    {"name": "name1", "required": "true"}
                                     ]
                         },
                     "action2":
                        { "options": [
                                    {"name": "name2", "required": "false", "default": "my_name"}
                                     ]
                        }
                    }
                }
            }


    with open(JSON_FILE, 'w') as f:
        f.write(json.dumps(data, f, indent=2))

    SCRIPT_DATA = """#!/usr/bin/python
\"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
\"""
from lib import defaults

def %s_action1(section_dict):
    return section_dict, defaults.YML_NAME

def %s_action1(section_dict):
    return section_dict, defaults.YML_NAME
""" % (feature, feature)

    with open(PYTHON_SCRIPT, 'w') as f:
        f.write(SCRIPT_DATA)

    print "\nINFO: New feature addition successful. Edit the files %s, "\
    "%s  and add the necessary ansible playbooks to use "\
    "them." %(JSON_FILE, PYTHON_SCRIPT)
