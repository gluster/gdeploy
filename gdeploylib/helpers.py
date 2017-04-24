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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.
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
import argparse
import ConfigParser
try:
    import yaml
except ImportError:
    print "Error: Package PyYAML not found."
    sys.exit(0)
from global_vars import Global
from yaml_writer import YamlWriter
from defaults import feature_list

# Imports needed to call the ansible api
from collections import namedtuple

# On RHEL6 we do not add ansible as a dependency, gdeploy gets
# installed whether ansible is installed or not, in such cases don't
# traceback but throw a decent error message. We do not exit in Except
# block, so as to allow harmless options like --version to work.
try:
    from ansible.parsing.dataloader import DataLoader
    from ansible.vars import VariableManager
    from ansible.inventory import Inventory
    from ansible.playbook.play import Play
    from ansible.executor.task_queue_manager import TaskQueueManager
    from ansible.errors import AnsibleError
except ImportError:
    print "Error: Ansible(>= 2.2) is not installed."
    print "Some of the features might not work if not installed.\n"

class Helpers(Global, YamlWriter):

    '''
    Some helper methods to help in directory/file creation/removal etc.
    '''

    def is_present_in_yaml(self, filename, item):
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

    def cleanup_and_quit(self, ret=1):
        if os.path.isdir(Global.base_dir) and not Global.keep:
            shutil.rmtree(Global.base_dir)
            Global.logger.info("Deleting playbook data %s"%Global.base_dir)
        else:
            print "You can view the generated configuration files "\
                "inside %s" % Global.base_dir
            Global.logger.info("Configuration saved inside %s" %Global.base_dir)
        Global.logger.info("Terminating gdeploy...")
        sys.exit(ret)

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
                msg = "Error: File copying failed(%s)" % e
                print msg
                Global.logger.error(msg)
                self.cleanup_and_quit()
        Global.logger.info("Copied files from %s to %s"%
                           (source_dir, Global.base_dir))

    def get_file_dir_path(self, basedir, newdir):
        return os.path.join(os.path.realpath(basedir), newdir)

    def uppath(self, path, n):
        # To get the n the parent of a particular directory
        return os.sep.join(path.split(os.sep)[:-n])

    def format_values(self, option_dict, excemption=''):
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

    def set_default_values(self, dictname, default_value_dict):
        for key, value in default_value_dict.iteritems():
            if key not in dictname:
                dictname[key] = value
        return dictname

    def is_option_present(self, param, section_dict, reqd=True):
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

    def get_hostnames(self):
        hosts = self.config_get_options('hosts', False)
        for host in hosts:
            Global.hosts += self.parse_patterns(host)
        self.remove_from_sections('hosts')

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
                print "Error: " + msg
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
                try:
                    options = Global.sections[self.current_host].get(section)
                except:
                    msg = "Error: Couldn't find value for %s option for "\
                          "host %s" %(section, self.current_host)
                    print msg
                    Global.logger.error(msg)
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
                try:
                    Global.master = [hostname[0]]
                except:
                    pass
                return val_group.group(2)
        return val


    def split_brickname_and_hostname(self, brick):
        if not brick:
            return None
        brk_group = re.search("(.*):(.*)", brick)
        if not brk_group:
            msg = "Error: Brick names should be in the format " \
                  "<hostname>:<brickname>. Exiting!"
            print msg
            Global.logger.error(msg)
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
            names = [pat_group.group(1) + name + pat_group.group(3)
                     for name in pat_string]

        elif '..' in pat_group.group(2):
            pat_string = pat_group.group(2).split('..')
            try:
                pat_string = map(int, pat_string)
                pat_string[-1] += 1
                range_func = range
            except:
                range_func = self.char_range
            pattern_string = [str(val) for val in range_func(pat_string[0],
                                                             pat_string[1])]
            names = [pat_group.group(1) + name + pat_group.group(3)
                     for name in pattern_string]
        else:
            msg = "Unknown pattern."
            print "Error: " + msg
            Global.logger.error(msg)
        return filter(None, names)


    def char_range(self, c1, c2):
        """Generates the characters from `c1` to `c2`, inclusive."""
        for c in xrange(ord(c1), ord(c2)+1):
            yield chr(c)

    def unique(self, mylist):
        uniquelist = []
        [uniquelist.append(item) for item in mylist if item not in
                uniquelist]
        return uniquelist


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


    def get_section_dict(self, section_dict, pattern):
        d = []
        for k, v in section_dict.iteritems():
            if re.search(pattern, k):
                d.append(v)
        return d

    def get_section_pattern(self, section):
        regexp = '(.*):(.*)'
        sec = re.match(regexp, section)
        if sec:
            Global.current_hosts = self.pattern_stripping(sec.group(2))
            section = sec.group(1)
        section = section.lower().replace('-', '_')
        section = [v for v in feature_list if re.match(v, section)]
        if not section:
            return False
        if len(section) > 1:
            msg = "Error: Oops! gdeploy is a bit confused with the " \
                  "section name %s. Please check your configuration file."\
                  %section
            Global.logger.error(msg)
            print msg
            self.cleanup_and_quit()
        return section[0]

    def remove_from_sections(self, regexp):
        r = re.compile(regexp)
        section_names = filter(r.match, Global.sections)
        map(Global.sections.__delitem__, section_names)

    def run_playbook(self, yaml_file, section_dict=None):
        self.create_inventory()
        if hasattr(self, 'section_dict'):
            if not section_dict:
                section_dict = self.section_dict
        if section_dict:
            section_dict['master'] = Global.master
            self.filename = Global.group_file
            self.create_var_files(section_dict)
        yml = self.get_file_dir_path(Global.base_dir, yaml_file)
        Global.logger.info("Invoking playbook  %s", yml)
        self.exec_ansible(yml)


    def exec_ansible(self, playbooks_file):
        if Global.new:
            self.exec_ansible_api(playbooks_file)
        else:
            self.exec_ansible_legacy(playbooks_file)

    def exec_ansible_api(self, playbooks_file):
        variable_manager = VariableManager()
        loader = DataLoader()

        ds = loader.load_from_file(playbooks_file)
        Options = namedtuple('Options', ['connection','module_path', 'forks',
                                         'remote_user', 'private_key_file',
                                         'ssh_common_args', 'ssh_extra_args',
                                         'sftp_extra_args', 'scp_extra_args',
                                         'become', 'become_method',
                                         'become_user', 'verbosity',
                                         'check'])
        options = Options(connection='ssh', module_path=None, forks=100,
                          remote_user='root', private_key_file='id_rsa',
                          ssh_common_args=None, ssh_extra_args=None,
                          sftp_extra_args=None, scp_extra_args=None,
                          become=None, become_method=None, become_user=None,
                          verbosity=None, check=False)

        # create inventory and pass to var manager
        inventory = Inventory(loader=loader, variable_manager=variable_manager,
                              host_list=Global.inventory)
        variable_manager.set_inventory(inventory)

        # Currently we are limiting to one playbook
        play_source = ds[0]
        play = Play().load(play_source, variable_manager=variable_manager,
                           loader=loader)

        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=loader,
                options=options,
                passwords=None,
                stdout_callback=Global.display
            )
            result = tqm.run(play)
            # Exit gdeploy in case of errors and user has explicitly set
            # not to ignore errors
            if result != 0 and Global.ignore_errors != 'yes':
                msg = "Error while executing playbook %s, exiting"\
                      %playbooks_file
                print msg
                Global.logger.error(msg)
                self.cleanup_and_quit(1)
            elif result != 0 and Global.ignore_errors == 'yes':
                msg = "Error while executing playbook %s, ignoring errors..."\
                      %playbooks_file
                Global.logger.error(msg)
                print msg
        except AnsibleError, e:
            print "%s"%e
        finally:
            if tqm is not None:
                tqm.cleanup()

    def exec_ansible_legacy(self, playbooks_file):
        executable = 'ansible-playbook'
        command = [executable, '-i', Global.inventory, Global.verbose,
                playbooks_file]
        command = filter(None, command)
        try:
            retcode = subprocess.call(command, shell=False)
            # Exit gdeploy in case of errors and user has explicitly set
            # not to ignore errors
            if retcode != 0 and Global.ignore_errors != 'yes':
                self.cleanup_and_quit(1)
            elif retcode != 0 and Global.ignore_errors == 'yes':
                print "Ignoring errors..."
        except (OSError, subprocess.CalledProcessError) as e:
            msg = "Error: Command %s failed. (Reason: %s)" % (cmd, e)
            Global.logger.error(msg)
            print msg
            sys.exit()


    def listify(self, var):
        if not var:
            return []
        if not type(var) is list:
            return [var]
        return var

    def correct_brick_format(self, brick_list):
        bricks = []
        for brick in brick_list:
            if not brick.startswith('/dev/'):
                bricks.append('/dev/' + brick)
            else:
                bricks.append(brick)
        return bricks

    def volname_formatter(self, section_dict):
        volname = section_dict.get('volname')
        if not volname:
            return section_dict
        section_dict['volname'] = self.split_volume_and_hostname(volname)
        return section_dict

    def perf_spec_data_write(self):
        '''
        Now this one looks dirty. Couldn't help it.
        This one reads the performance related data like
        number of data disks and stripe unit size  if
        the option disk type is provided in the config.
        Some calculations are made as to enhance
        performance
        '''
        disktype = self.config_get_options('disktype', False)
        if disktype:
            perf = dict(disktype=disktype[0].lower())
            # Supported disk types
            sdisks = ['raid10', 'raid5', 'raid6', 'jbod']
            if perf['disktype'] not in sdisks:
                msg = "Unsupported disk type!\nOnly %s are supported"%sdisks
                print "Error: " + msg
                Global.logger.error(msg.replace("\n", " "))
                self.cleanup_and_quit()
            if perf['disktype'] != 'jbod':
                diskcount = self.config_get_options('diskcount', True)
                perf['diskcount'] = int(diskcount[0])
                stripe_size = self.config_get_options('stripesize', False)
                if not stripe_size and perf['disktype'] == 'raid6':
                    msg = "Error: 'stripesize' not provided for disktype %s"\
                          % perf['disktype']
                    print msg
                    Global.logger.error(msg)
                    self.cleanup_and_quit()
                if stripe_size:
                    perf['stripesize'] = int(stripe_size[0])
                    if perf['disktype'] == 'raid10' and perf[
                            'stripesize'] != 256:
                        warn = "Warning: We recommend a stripe unit size of 256KB " \
                            "for RAID 10"
                        Global.logger.warning(warn)
                else:
                    perf['stripesize'] = 256
                perf['dalign'] = {
                    'raid6': perf['stripesize'] * perf['diskcount'],
                    'raid5': perf['stripesize'] * perf['diskcount'],
                    'raid10': perf['stripesize'] * perf['diskcount']
                }[perf['disktype']]
            else:
                perf['dalign'] = 256
                perf['diskcount'] = perf['stripesize'] = 0
        else:
            perf = dict(disktype='jbod')
            perf['dalign'] = 256
            perf['diskcount'] = perf['stripesize'] = 0
        self.create_var_files(perf, False, Global.group_file)

    def create_inventory(self):
        if not os.path.isfile(Global.inventory):
            self.touch_file(Global.inventory)
        Global.current_hosts and self.write_config(
            Global.group,
            Global.current_hosts,
            Global.inventory)
        try:
            if not Global.master:
                # We set the `master' variable in group_vars/all file here.
                # If brick_hosts are present use one of them as master.
                # Else use one from Global.current_hosts.
                #
                # Previous solution: [list(set(Global.current_hosts) - set(
                # Global.brick_hosts))[0]] fails when length of
                # Global.current_hosts was equal to Global.brick_hosts
                # Or less than Global.brick_hosts
                if Global.brick_hosts:
                    Global.master = Global.brick_hosts[0]
                else:
                    Global.master = Global.current_hosts[0]
        except:
            pass
        try:
            hostname = Global.master or Global.current_hosts[0]
        except:
            msg = "Warning: Insufficient host names or IPs. Running  " \
                  "in the localhost"
            print msg
            Global.logger.warn(msg)
            hostname = "127.0.0.1"
        self.write_config('master', hostname, Global.inventory)

    def call_config_parser(self):
        config = ConfigParser.ConfigParser(allow_no_value=True)
        config.optionxform = str
        return config

    def remove_section(self, filename, section):
        config = self.read_config(filename)
        try:
            config.remove_section(section)
        except:
            pass
        with open(filename, 'w+') as out:
            config.write(out)

    def read_config(self, config_file):
        config_parse = self.call_config_parser()
        try:
            config_parse.read(config_file)
            return config_parse
        except:
            msg = "Sorry! Looks like the format of configuration " \
                  "file %s is not something we could read! \nTry removing " \
                  "whitespaces or unwanted characters in the configuration " \
                  "file." % config_file
            print msg
            Global.logger.error(msg)
            self.cleanup_and_quit()

    def write_to_inventory(self, section, options):
        self.write_config(section, options, Global.inventory)

    def write_config(self, section, options, filename):
        self.remove_section(filename, section)
        config = self.call_config_parser()
        config.add_section(section)
        if type(options) is not dict:
            options = self.pattern_stripping(options)
            for option in options:
                config.set(section, option)
        else:
            for k, v in options.iteritems():
                v = ','.join(self.pattern_stripping(v))
                config.set(section, k , v)
        try:
            with open(filename, 'ab') as f:
                config.write(f)
        except:
            msg = "Error: Failed to create file %s. Exiting!" % filename
            print msg
            Global.logger.error(msg)
            self.cleanup_and_quit()

    def config_section_map(
            self,
            section,
            option,
            required=False):
        try:
            return Global.config.get(section, option)
        except:
            if required:
                msg = "Error: Option %s not found! Exiting!" % option
                Global.logger.error(msg)
                print msg
                self.cleanup_and_quit()
            return []

    def get_option_dict(self, config_parse, section, required=False):
        try:
            return config_parse.items(section)
        except:
            if required:
                msg = "Error: Section %s not found in the " \
                      "configuration file" % section
                Global.logger.error(msg)
                print msg
                self.cleanup_and_quit()
            return []

    def config_get_options(self, section, required):
        try:
            return Global.config.options(section)
        except ConfigParser.NoSectionError as e:
            if required:
                msg = "Error: Section %s not found in the " \
                      "configuration file" % section
                Global.logger.error(msg)
                print msg
                self.cleanup_and_quit()
            return []

    def config_get_sections(self, config_parse):
        try:
            return config_parse.sections()
        except:
            msg = "Error: Looks like you haven't provided any options " \
                  "needed in the conf " \
                  "file. Please populate the conf file and retry!"
            Global.logger.error(msg)
            print msg
            self.cleanup_and_quit()

    def split_string(self, string, sep):
        """Split a string separated by sep

        Return a list of tokens."""
        pattern = r'((?:[^'+sep+'\\\\]+'+sep+'\\\\.)*)(['+sep+'])?'
        regex = re.compile(pattern)
        result = []

        for match in regex.finditer(string):
            result.append(match.group(1))
            if (not match.group(2)):
                break
        return result

    def get_thin_pool_chunk_sz(self):
        # As per perf recommendations
        #
        # For RAID-6 storage, the striping parameters should be chosen so that
        # the full stripe size (stripe_unit size * number of data disks) is
        # between 1 MiB and 2 MiB, preferably in the low end of the range. The
        # thin pool chunk size should be chosen to match the RAID 6 full stripe
        # size. Matching the chunk size to the full stripe size aligns thin
        # pool allocations with RAID 6 stripes, which can lead to better
        # performance. Limiting the chunk size to below 2 MiB helps reduce
        # performance problems due to excessive copy-on-write when snapshots
        # are used.
        #
        # For example, for RAID 6 with 12 disks (10 data disks), stripe unit
        # size should be chosen as 128 KiB. This leads to a full stripe size of
        # 1280 KiB (1.25 MiB). The thin pool should then be created with the
        # chunk size of 1280 KiB.
        #
        # For RAID 10 storage, the preferred stripe unit size is 256 KiB. This
        # can also serve as the thin pool chunk size. Note that RAID 10 is
        # recommended when the workload has a large proportion of small file
        # writes or random writes. In this case, a small thin pool chunk size
        # is more appropriate, as it reduces copy-on-write overhead with
        # snapshots.
        #
        # For JBOD, use a thin pool chunk size of 256 KiB.

        disktype = self.config_get_options('disktype', False) or 'jbod'
        disktype = self.get_first_index(disktype)
        stripe_unit_size = self.config_get_options('stripesize', False) or ''
        stripe_unit_size = self.get_first_index(stripe_unit_size)
        diskcount = self.config_get_options('diskcount', False) or ''
        diskcount = self.get_first_index(diskcount)

        if disktype == 'raid6':
            # If user has ommited chunk size or stripe unit size, we leave
            # it blank and let the system determine proper default value.
            if stripe_unit_size.strip() == '' or diskcount.strip() == '':
                return ''
            try:
                chunksize = str(int(stripe_unit_size) * int(diskcount)) + 'K'
            except ValueError:
                print "Only integer value is supported for stripesize or \
                diskcount!"
                print "Found %s and %s"%(stripe_unit_size, diskcount)
                self.cleanup_and_quit()
        else:
            # As per performance recommendations for RAID 10 storage, the
            # preferred thin pool chunk size is 256K, to override user is
            # expected to set the chunksize variable in config.
            chunksize = '256K'
        return chunksize

    def get_first_index(self, list_item):
        if type(list_item) == list:
            return list_item[0]
        else:
            return list_item
