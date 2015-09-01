#!/usr/bin/python
# -*- coding: utf-8 -*-
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
#    helpers.py
#    ---------
#    Helpers consists of a couple of general helper methods
#    called from various parts of the framework to create directories
#    and run commands
#

import os
import re
import sys
import itertools
try:
    import yaml
except ImportError:
    print "Error: Package PyYAML not found."
    sys.exit(0)
from global_vars import Global


class Helpers(Global):

    '''
    Some helper methods to help in directory/file creation/removal etc.
    '''

    def present_in_yaml(self, filename, item):
        doc = self.read_yaml(filename)
        if doc and item in doc:
            return True
        return False

    def get_value_from_yaml(self, filename, item):
        doc = self.read_yaml(filename)
        return doc.get(item)

    def read_yaml(self, filename):
        with open(filename, 'r') as f:
            return yaml.load(f)

    def cleanup_and_quit(self):
        if os.path.isdir(Global.base_dir):
            self.exec_cmds('rm -rf', Global.base_dir)
        sys.exit(0)

    def mk_dir(self, direc):
        if os.path.isdir(direc):
            self.exec_cmds('rm -rf', direc)
        self.exec_cmds('mkdir', direc)

    def touch_file(self, filename):
        try:
            os.remove(filename)
        except OSError:
            pass
        self.exec_cmds('touch', filename)

    def get_file_dir_path(self, basedir, newdir):
        return os.path.join(os.path.realpath(basedir), newdir)

    def uppath(self, path, n):
        # To get the n the parent of a particular directory
        return os.sep.join(path.split(os.sep)[:-n])

    def fix_format_of_values_in_config(self, option_dict, excemption=''):
        '''
        This method will split the values provided in config by user,
        when parsed as a dictionary
        '''
        for key, value in option_dict.iteritems():
            '''
            HACK: The value for option 'transport' can have comma in it,
            eg: tcp,rdma. so comma here doesn't mean that it can have
            multiple values. Hence the excemption argument
            '''
            if ',' in str(value) and key not in [excemption]:
                option_dict[
                    key] = self.split_comma_seperated_options(value)
        return option_dict

    def set_default_value_for_dict_key(self, dictname, default_value_dict):
        for key, value in default_value_dict.iteritems():
            if key not in dictname:
                dictname[key] = value

    def check_for_param_presence(self, param, section_dict, reqd=True):
        if not section_dict.get(param):
            if reqd:
                print "Error: %s not provided in the config. " \
                        "Cannot continue!" % param
                self.cleanup_and_quit()
            return False

    def get_options(self, config, section, required):
        if self.filetype == 'group_vars':
            return self.config_get_options(config, section, required)
        else:
            options = self.config_section_map(
                config, self.filename.split('/')[-1], section, required)
            return self.split_comma_seperated_options(options)

    def split_comma_seperated_options(self, options):
        if options:
            return filter(None, options.split(','))
        return []

    def split_val_and_hostname(self, val, georep=False):
        '''
        This gives the user the flexibility to not give the hosts
        section. Instead one can just specify the volume name
        with one of the peer member's hostname or IP in the
        format <hostname>:<volumename>
        '''
        if val:
            val_group = re.search("(.*):(.*)", val)
            if val_group:
                hostname = self.parse_patterns(val_group.group(1))
                Global.hosts = [host for host in Global.hosts if
                        host not in hostname]
                if grorep:
                    return hostname, val_group.group(2)
                try:
                    Global.master = [Global.hosts[0]]
                except:
                    Global.master = [hostname[0]]
                for host in hostname:
                    Global.hosts.append(host)
                    Global.brick_hosts.append(host)
                return val_group.group(2)
        return val


    def format_brick_names(self, bricks):
        ultimate_brickname = []
        brick_list, whole_bricks = [], []
        if not isinstance(bricks, list):
            bricks = [bricks]
        for brick in bricks:
            brick_list.append(self.split_val_and_hostname(brick))
            for brk in brick_list:
                whole_bricks += self.parse_patterns(brk)
            for brk, hst in itertools.product(whole_bricks, Global.brick_hosts):
                ultimate_brickname.append(hst + ":" + brk)
        return ultimate_brickname


    def pattern_stripping(self, values):
        value_list = []
        if not isinstance(values, list):
            return self.parse_patterns(values)
        else:
            for value in values:
                value_list += self.parse_patterns(value)
            return value_list

    def parse_patterns(self, pattern):
        '''
        This method can be used to parse patterns given in
        hostnames, IPs ets. patterns should be of the format
        10.70.46.1{3..7} or myvm.remote.in.vm{a..f}
        '''
        if not pattern:
            return None
        pat_group = re.search("(.*){(.*)}(.*)", pattern)
        if not pat_group:
            return [pattern]
        pat_string = pat_group.group(2).split('..')
        try:
            pat_string = map(int, pat_string)
            pat_string[-1] += 1
            range_func = range
        except:
            range_func = self.char_range
        pattern_string = [str(val) for val in range_func(pat_string[0], pat_string[1])]
        names = [pat_group.group(1) + name + pat_group.group(3) for name in pattern_string]
        return filter(None, names)


    def char_range(self, c1, c2):
        """Generates the characters from `c1` to `c2`, inclusive."""
        for c in xrange(ord(c1), ord(c2)+1):
            yield chr(c)

    def exec_cmds(self, cmd, opts):
        try:
            os.system(cmd + ' ' + opts)
        except:
            print "Error: Command %s failed. Exiting!" % cmd
            sys.exit()
