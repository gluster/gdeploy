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

import os, json
from helpers import Helpers
from yaml_writer import YamlWriter
from global_vars import Global
from gdeploy import get_hostnames
import features

helpers = Helpers()
yaml_writer = YamlWriter()

def call_features():
    global helpers
    if not Global.sections:
        return
    get_hostnames()
    Global.current_hosts = Global.hosts
    map(get_feature_dir, Global.sections)

def get_feature_dir(section):
    global helpers
    section_dir = os.path.join(features.__path__[0], section)
    if not os.path.isdir(section_dir):
        return
    config_file = helpers.get_file_dir_path(section_dir, section + '.json')
    if not os.path.isfile(config_file):
        print "Error: Setup file not found for feature '%s'" % section
        return
    section_dict = parse_the_user_config(section, section_dir)
    feature_func = getattr(features, section)
    feature_mod = getattr(feature_func, section)
    feature_call = getattr(feature_mod, section + '_' + section_dict[
        'action'].replace('-', '_'))
    section_dict, yml = feature_call(section_dict)
    yaml_writer.create_var_files(section_dict)
    helpers.run_playbook(yml)

def parse_the_user_config(section, section_dir):
    global helpers
    section_dict = Global.sections[section]
    section_dict = helpers.format_values(section_dict)
    action_dict = get_action_data(section, section_dir, section_dict)
    if not action_dict:
        return
    reqd_vals = get_required_values(action_dict["options"])
    default_dict = get_default_values(action_dict["options"])
    helpers.set_default_values(section_dict, default_dict)
    section_dict = validate_the_user_data(section_dict, reqd_vals)
    section_dict['action'] = section_dict.pop('action').replace('-', '_')
    if not section_dict:
        helpers.cleanup_and_quit()
    get_hostnames()
    return section_dict

def get_action_data(section, section_dir, section_dict):
    global helpers
    json_file = helpers.get_file_dir_path(section_dir, section + '.json')
    json_data = open(json_file)
    data = json.load(json_data)
    json_data.close()
    action_dict = data[section]["action"][section_dict.get("action")]
    if not action_dict:
        print "\nError: We could not find the operations corresponding " \
                "to the action specified. Check your configuration file"
        return False
    else:
        return action_dict


def get_required_values(value_dict):
    reqd_vals = []
    for hval in value_dict:
        if hval["required"] == "true":
            reqd_vals.append(hval["name"])
    return reqd_vals


def get_default_values(value_dict):
    def_vals = {}
    for hval in value_dict:
        if hval.get("default"):
            def_vals[hval["name"]] = hval["default"]
    return def_vals

def validate_the_user_data(section_dict, reqd_vals):
    for val in reqd_vals:
        if type(val) is not list:
            if not section_dict.get(val):
                print "\nError: configuration file validation error. "\
                        "\nRequired option %s not found." % val
                return False
            return section_dict
        else:
            check = [True for each in val if section_dict.get(each)]
            if True not in check:
                print "\nError: configuration file validation error. "\
                        "\nAny one of the options in %s required." % val
                return False
            for each in val:
                if not section_dict.get(each):
                    section_dict[each] = None
            return section_dict


