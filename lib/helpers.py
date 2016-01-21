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
import subprocess
import re
import sys
import itertools
import shutil
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
        if not os.path.isfile(filename):
            return
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
            shutil.rmtree(Global.base_dir)
        sys.exit(0)

    def mk_dir(self, direc):
        if os.path.isdir(direc):
            shutil.rmtree(direc)
        os.makedirs(direc)

    def touch_file(self, filename):
        try:
            os.remove(filename)
        except OSError:
            pass
        os.mknod(filename)

    def copy_files(self, source_dir):
        files = os.listdir(source_dir)
        files_to_move = [self.get_file_dir_path(source_dir, f) for f in files]
        for each in files_to_move:
            try:
                shutil.copy(each, Global.base_dir)
            except IOError as e:
                print "\nError: File copying failed(%s)" % e
                self.cleanup_and_quit()

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
                    key] = self.split_comma_separated_options(value)
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

    def split_comma_separated_options(self, options):
        if options:
            pat_group = re.search("(.*){(.*)}(.*)", options)
            if not pat_group:
                return filter(None, options.split(','))
            else:
                result = []
                for i in range(1,3):
                    if i == 2:
                        result[-1] += '{' + pat_group.group(2) + '}'
                    else:
                        result.extend(pat_group.group(i).split(','))
                return self.pattern_stripping(result)
        return []

    def validate_hostname_volume_pattern(self, val):
        val_group = re.search("(.*):(.*)", val)
        if not val_group:
            return False
        return True


    def get_var_file_type(self):
        '''
        Decides if host_vars are to be created or everything can
        fit into the group_vars file based on the options provided
        in the configuration file. If all the hostnames are
        present as sections in the configuration file, assumes
        we need host_vars. Fails accordingly.
        '''
        if set(Global.hosts).intersection(set(Global.sections)):
            if set(Global.hosts).issubset(set(Global.sections)):
                Global.var_file = 'host_vars'
            else:
                msg =  "Looks like you missed to give configurations " \
                    "for one or many host(s). Exiting!"
                print "\nError: " + msg
                Global.logger.error(msg)
                self.cleanup_and_quit()
            return True
        elif 'devices' in self.sections or 'brick_dirs' in self.sections:
            Global.var_file = 'group_vars'
            return True
        else:
            return False

    def get_options(self, section, required=False):
        if hasattr(Global, 'var_file') and Global.var_file:
            if Global.var_file == 'group_vars':
                return self.config_get_options(section, required)
            else:
                options = self.config_section_map(
                    self.current_host, section, required)
                return self.split_comma_separated_options(options)
        return self.section_dict.get(section)

    def split_volume_and_hostname(self, val):
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
                if not self.config_section_map('volume',
                        'action', False) == 'add-brick':
                    for host in hostname:
                        if host not in Global.hosts:
                            Global.hosts.append(host)
                try:
                    Global.master = [hostname[0]]
                except:
                    pass
                return val_group.group(2)
        return val


    def split_georep_volname(self, val):
        if val:
            val_group = re.search("(.*):(.*)", val)
            if val_group:
                hostname = self.parse_patterns(val_group.group(1))
                if not len(hostname) == 1:
                    err = "Provide only one hostname for master or slave volume"
                    print "\nError: " + err
                    Global.logger.error(msg)
                    self.cleanup_and_quit()
                return hostname, val_group.group(2)
            err = "Provide master volume name and slave volume name in the "\
                    "format <hostname>:<volume name>"
            print "\nError: " + msg
            Global.logger.error(msg)
            self.cleanup_and_quit()


    def split_brickname_and_hostname(self, brick):
        if not brick:
            return None
        brk_group = re.search("(.*):(.*)", brick)
        if not brk_group:
            print "\nError: Brick names should be in the format " \
                    "<hostname>:<brickname>. Exiting!"
            self.cleanup_and_quit()
        if brk_group.group(1) not in Global.brick_hosts:
            Global.brick_hosts.append(brk_group.group(1))
        return brk_group.group(2)


    def format_brick_names(self, bricks):
        ultimate_brickname, Global.brick_hosts = [], []
        brick_list, whole_bricks = [], []
        if not isinstance(bricks, list):
            bricks = [bricks]
        for brick in bricks:
            brick_list.append(self.split_brickname_and_hostname(brick))
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
        if ',' in pat_group.group(2):
            pat_string = pat_group.group(2).split(',')
            names = [pat_group.group(1) + name + pat_group.group(3) for name in pat_string]

        elif '..' in pat_group.group(2):
            pat_string = pat_group.group(2).split('..')
            try:
                pat_string = map(int, pat_string)
                pat_string[-1] += 1
                range_func = range
            except:
                range_func = self.char_range
            pattern_string = [str(val) for val in range_func(pat_string[0], pat_string[1])]
            names = [pat_group.group(1) + name + pat_group.group(3) for name in pattern_string]
        else:
            msg = "Unknown pattern."
            print "\nError: " + msg
            Global.logger.error(msg)
        return filter(None, names)


    def char_range(self, c1, c2):
        """Generates the characters from `c1` to `c2`, inclusive."""
        for c in xrange(ord(c1), ord(c2)+1):
            yield chr(c)



    def check_backend_setup_format(self):
        section_regexp = '^backend-setup(:)*(.*)'
        hosts = []
        backend_setup = False
        for section in Global.sections:
            val = re.search(section_regexp, section)
            if val:
                backend_setup = True
                if val.group(2):
                    hosts.append(val.group(2))
        return backend_setup, hosts


    def not_subdir(self, path, directory):
        if path.endswith('/'):
            path = path[:-1]
        base_dir = os.path.abspath(directory)
        is_subdir =  base_dir.startswith(path +
                '/') and base_dir != path
        return not is_subdir


    def get_section_dict(self, pattern):
        d = []
        for k, v in Global.sections.iteritems():
            if re.search(pattern, k):
                d.append(v)
        return d

    def remove_from_sections(self, regexp):
        r = re.compile(regexp)
        section_names = filter(r.match, Global.sections)
        map(Global.sections.__delitem__, section_names)

    def run_playbook(self, yaml_file):
        self.create_inventory()
        self.iterate_dicts_and_yaml_write(self.section_dict)
        yml = self.get_file_dir_path(Global.base_dir, yaml_file)
        self.exec_ansible_cmd(yml)

    def create_inventory(self):
        self.touch_file(Global.inventory)
        Global.current_hosts and self.write_config(
            Global.group,
            Global.current_hosts,
            Global.inventory)
        if not Global.master or Global.master in Global.brick_hosts:
            try:
                Global.master = [list(set(Global.current_hosts) - set(
                    Global.brick_hosts))[0]]
            except:
                Global.master = None
        if Global.current_hosts or Global.master:
            self.write_config('master', Global.master or [Global.current_hosts[0]],
                              Global.inventory)

    def exec_ansible_cmd(self, playbooks_file=Global.playbooks_file):
        executable = 'ansible-playbook'
        command = [executable, '-i', Global.inventory, Global.verbose,
                playbooks_file]
        command = filter(None, command)
        try:
            subprocess.call(command, shell=False)
        except (OSError, subprocess.CalledProcessError) as e:
            print "Error: Command %s failed. (Reason: %s)" % (cmd, e)
            sys.exit()
