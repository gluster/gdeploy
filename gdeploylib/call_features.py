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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.
#

import os
import json
from helpers import Helpers
from yaml_writer import YamlWriter
from global_vars import Global
import gdeployfeatures

helpers = Helpers()
yaml_writer = YamlWriter()
section_name = None


def call_features():
    global helpers
    if not Global.sections:
        msg = "No sections found in config file. Exiting!"
        print "Error: " + msg
        Global.logger.error(msg)
        return
    helpers.get_hostnames()
    map(get_feature_dir, Global.sections)


def get_feature_dir(section):
    '''
    Each of the unique section in the configuration file is parsed,
    calling corresponding function, and ultimately running the ansible
    playbook returned back by the function
    '''
    global helpers, section_name
    Global.master = None
    Global.current_hosts = Global.hosts
    section_name = helpers.get_section_pattern(section)

    if not section_name:
        # We do not log this, since many features like disktype, raid do not
        # have their own section directories under gdeployfeature
        return

    try:
        section_dir = os.path.join(gdeployfeatures.__path__[0], section_name)
    except:
        msg = "Error: Could not find the installation path for "\
              "`gdeployfeatures' module. Please check gdeploy installation."
        print msg
        Global.logger.error(msg)
        helpers.cleanup_and_quit()

    if not os.path.isdir(section_dir):
        msg = "Feature directory `%s' not found" % section_dir
        Global.logger.error(msg)
        print "Error: " + msg
        return

    config_file = helpers.get_file_dir_path(section_dir, section_name +
                                            '.json')
    if not os.path.isfile(config_file):
        msg = "Error: Setup file %s not found for feature `%s'" % (
            config_file, section)
        Global.logger.error(msg)
        print msg
        return

    section_dict = parse_the_user_config(section, section_dir)
    if not section_dict:
        return

    feature_func = getattr(gdeployfeatures, section_name)
    feature_mod = getattr(feature_func, section_name)
    try:
        feature_call = getattr(feature_mod, section_name + '_' + section_dict[
            'action'].replace('-', '_'))
    except:
        print "Error: No method found for action %s" % (section_name +
                                                        '_' + section_dict['action'])
        helpers.cleanup_and_quit()

    section_dict, yml = feature_call(section_dict)

    if section_dict == False or section_dict == None or section_dict == {}:
        return

    for key in section_dict.keys():
        section_dict[key.replace('-', '_')] = section_dict.pop(key)

    if (section_dict and yml):
        if type(yml) is list:
            for each in yml:
                helpers.run_playbook(each, section_dict)
        else:
            helpers.run_playbook(yml, section_dict)


def parse_the_user_config(section, section_dir):
    '''
    Validates the configuration file comparing it with the feature JSON
    '''

    global helpers
    section_dict = Global.sections[section]
    section_dict = helpers.format_values(section_dict)

    action_dict = get_action_data(section, section_dir, section_dict)
    if not action_dict:
        return False

    options = action_dict.get("options")
    if not options or not options[0]:
        return section_dict

    reqd_vals = get_required_values(options)
    default_dict = get_default_values(options)
    section_dict = helpers.set_default_values(section_dict, default_dict)
    section_dict = validate_the_user_data(section_dict, reqd_vals)

    if not section_dict:
        return False

    section_dict['action'] = section_dict.pop('action').replace('-', '_')

    if not section_dict:
        helpers.cleanup_and_quit()

    helpers.get_hostnames()
    return section_dict


def get_action_data(section, section_dir, section_dict):
    global helpers, section_name
    json_file = helpers.get_file_dir_path(section_dir, section_name + '.json')
    Global.logger.info("Parsing json file: %s" % json_file)
    json_data = open(json_file)
    data = json.load(json_data)
    if Global.trace:
        Global.logger.info("Found json data: %s" % data)
    json_data.close()
    action_dict = data[section_name]["action"].get(section_dict.get("action"))
    if not action_dict:
        msg = "Warning: We could not find the operations corresponding " \
              "to the action specified for the section {0}. "\
              "Skipping this section.".format(section_name)
        print msg
        Global.logger.warning(msg)  # delete leading newline
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
                msg = "Configuration file validation error. "
                msg1 = "Required option %s not found." % val
                Global.logger.error(msg.lstrip() + msg1.lstrip())
                print "Error: " + msg + "\n" + msg1
                return False
            continue
        else:
            check = [True for each in val if section_dict.get(each)]
            if True not in check:
                msg = "\nError: configuration file validation error. "\
                      "\nAny one of the options in %s required." % val
                Global.logger.error(msg.lstrip())
                print msg
                return False
            for each in val:
                if not section_dict.get(each):
                    section_dict[each] = None
    return section_dict
