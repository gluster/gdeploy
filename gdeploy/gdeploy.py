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

import argparse
import sys
import os
import time
import shutil
from collections import OrderedDict
from lib import *
from core import call_core_functions


helpers = Helpers()

@logfunction
def parse_arguments(args=None):
    '''
    This method uses argparser to parse the command line inputs
    to the gdeploy script
    '''
    usage = 'gdeploy [-h] [-v] [-vv] [-c CONFIG_FILE] ' \
        '[-k]'
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s 1.0')
    parser.add_argument('-c', dest='config_file',
                        help="Configuration file",
                        type=argparse.FileType('rt'))
    parser.add_argument('-k', dest='keep',
                        action='store_true',
                        help="Keep the generated ansible utility files")
    parser.add_argument('--trace', dest='trace',
                        action='store_true',
                        help="Turn on the trace messages in logs")
    parser.add_argument('-vv', dest='verbose',
                        action='store_true',
                        help="verbose mode")
    parser.add_argument('--addfeature', dest='feature_name',
                        help="Add new feature to gdeploy")
    try:
        args = parser.parse_args(args=args)
    except IOError as msg:
        parser.error(str(msg))
    if not args.config_file:
        if not args.feature_name:
            parser.print_help()
            try:
                Global.logger.error("Invalid usage")
            except:
                pass
            return None
        else:
            add_feature(args.feature_name)
            return None
    return args

@logfunction
def init_global_values(args):
    global helpers
    Global.config = helpers.read_config(args.config_file.name)
    Global.verbose = '-vv' if args.verbose else ''
    Global.keep = args.keep
    Global.trace = args.trace
    for sec in  Global.config._sections:
        sections = helpers.parse_patterns(sec)
        for each in sections:
            Global.sections[each] = dict(Global.config._sections[sec])


@logfunction
def check_ansible_installation():
    ret = os.system('ansible --version 1>/dev/null 2>/dev/null')
    if ret:
        msg =  "gdeploy requires Ansible to run. \nPlease install " \
                "Ansible(version >= 1.9.2) to continue."
        print "Error: " + msg
        Global.logger.error(msg)
        return

@logfunction
def get_hostnames():
    global helpers
    hosts = helpers.config_get_options('hosts', False)
    for host in hosts:
        Global.hosts += helpers.parse_patterns(host)
    helpers.remove_from_sections('hosts')

@logfunction
def create_files_and_dirs():
    global helpers
    '''
    Create required directories for all the configuration files
    to go in. Since the client data for gluster confs are common for all the
    hosts, creating a group var file anyway.
    '''
    helpers.mk_dir(Global.group_vars_dir)
    helpers.touch_file(Global.group_file)
    helpers.mk_dir(Global.host_vars_dir)

@logfunction
def gdeploy_cleanup():
    '''
    Remove created temp directory if not explicitly asked to keep
    '''
    if not Global.keep:
        shutil.rmtree(Global.base_dir)
    else:
        print "\nYou can view the generated configuration files "\
            "inside %s" % Global.base_dir
        Global.logger.info("Configuration saved inside %s" %Global.base_dir)
    Global.logger.info("Terminating gdeploy...")

@logfunction
def create_playbooks_in_local():
    '''
    Templates directory in this codebase's repo will be moved to
    /var/tmp/playbooks
    '''
    global helpers
    templates_path_pkg = '/usr/share/ansible/gdeploy/playbooks'
    templates_env_var = os.getenv('GDEPLOY_TEMPLATES')
    # Is environment variable GDEPLOY_TEMPLATES set
    if templates_env_var:
        templates_dir = helpers.get_file_dir_path(templates_env_var,
                'playbooks')
    # Or assumes the templates are present as a part of ansible installation
    else:
        templates_dir = templates_path_pkg
    if not os.path.isdir(templates_dir):
        msg = "Template files not found.\n\n" \
            "Gdeploy looks inside the directory %s or \n" \
            "wants the environment varible GDEPLOY_TEMPLATES set."\
             % (templates_path_pkg)
        print "\nError: " + msg
        Global.logger.error(msg.strip('\n\t\r'))
        helpers.cleanup_and_quit()
    helpers.copy_files(templates_dir)

if __name__ == '__main__':
    '''
    This script just reads in the command line arguments and gets the
    config file.

    Here gdeploy starts!
    Drum roll!
    '''
    '''
    and it initialises a global var to keep track of the logs
    '''
    log_event()
    args = parse_arguments(sys.argv[1:])
    if args:
        check_ansible_installation()
        init_global_values(args)
        create_files_and_dirs()
        get_hostnames()
        create_playbooks_in_local()
        call_core_functions()
        call_features()
        gdeploy_cleanup()
