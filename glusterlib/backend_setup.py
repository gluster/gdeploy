#!/usr/bin/python
# -*- coding: utf-8 -*- #
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
#
#    yaml_writer.py
#    -------------
#    YamlWriter is a helper class used by VarFileGenerator to write
#    all the necessary sections and options into the yaml file
#    as per specified in the configuration file
#

from conf_parser import ConfigParseHelpers
from global_vars import Global
from helpers import Helpers
from yaml_writer import YamlWriter
import re
try:
    import yaml
except ImportError:
    msg = "Package PyYAML not found."
    print "\nError: " + msg
    Global.logger.error(msg)
    sys.exit(0)
import os


class BackendSetup(YamlWriter):

    def __init__(self, config):
        self.config = config
        self.section_dict = dict()
        self.write_sections()

    def write_sections(self):
        Global.logger.info("Reading configuration for backend setup")
        section_regexp = '^backend-setup(:)*(.*)'
        self.sections = self.config._sections
        hosts = []
        backend_setup = False
        for section in self.sections:
            val = re.search(section_regexp, section)
            if val:
                backend_setup = True
                if val.group(2):
                    hosts.append(val.group(2))
        self.bricks = []
        default = self.config_get_options(self.config,
                                               'default', False)
        if default:
            self.default = False if default[0].lower() == 'no' else True
        self.default = self.default if hasattr(self, 'default') else True
        if not backend_setup:
            if not self.get_var_file_type():
                return
            else:
                msg = "This configuration format will be deprecated  "\
                "in the next release.\nPlease refer the setup guide "\
                "for the new configuration format."
                print "Warning: " + msg
                Global.logger.warning(msg=msg)
                if self.var_file == 'host_vars':
                    for host in Global.hosts:
                        self.bricks = []
                        devices = self.config_section_map(self.config, host,
                                                  'devices', False)
                        self.filename = self.get_file_dir_path(Global.host_vars_dir, host)
                        self.touch_file(self.filename)
                        self.bricks = self.split_comma_seperated_options(devices)
                        ret = self.call_gen_methods()
                else:
                    self.filename =  Global.group_file
                    self.bricks = self.config_get_options(self.config,
                                                           'devices', False)
                    ret = self.call_gen_methods()

        else:
            hosts = filter(None, hosts)
            self.parse_section('')
            ret = self.call_gen_methods()
            self.var_file = 'group_vars'
            if hosts:
                self.var_file = None
                hosts = self.pattern_stripping(hosts)
                Global.hosts.extend(hosts)
                for host in hosts:
                    self.bricks = []
                    self.host_file = self.get_file_dir_path(Global.host_vars_dir, host)
                    self.touch_file(self.host_file)
                    self.parse_section(':' + host)
                    ret = self.call_gen_methods()
                self.var_file = 'host_vars'


        self.filename =  Global.group_file
        self.perf_spec_data_write()
        self.tune_profile()
        if not Global.hosts:
            print "Error: Hostnames not provided. Cannot continue!"
            self.cleanup_and_quit()
        Global.hosts = list(set(Global.hosts))
        if ret:
            msg = "Back-end setup triggered"
            Global.logger.info(msg)
            print "\nINFO: " + msg
            Global.var_file =  self.var_file

    def call_gen_methods(self):
        return self.write_mount_options()

    def get_var_file_type(self):
        '''
        Decides if host_vars are to be created or everything can
        fit into the group_vars file based on the options provided
        in the configuration file. If all the hostnames are
        present as sections in the configuration file, assumes
        we need host_vars. Fails accordingly.
        '''
        if set(Global.hosts).intersection(set(self.sections)):
            if set(Global.hosts).issubset(set(self.sections)):
                self.var_file = 'host_vars'
            else:
                msg =  "Looks like you missed to give configurations " \
                    "for one or many host(s). Exiting!"
                print "\nError: " + msg
                Global.logger.error(msg)
                self.cleanup_and_quit()
            return True
        elif 'devices' in self.sections:
            self.var_file = 'group_vars'
            return True
        else:
            return False

    def parse_section(self, hostname):
        try:
            self.section_dict = self.config._sections['backend-setup' +
                    hostname]
            del self.section_dict['__name__']
        except KeyError:
            return
        try:
            self.filename = self.host_file
        except:
            self.filename =  Global.group_file
        self.section_dict = self.fix_format_of_values_in_config(self.section_dict)

    def write_brick_names(self):
        if not self.bricks:
            self.bricks = self.section_dict.get('devices')
        if self.bricks:
            self.bricks = self.pattern_stripping(self.bricks)
            self.section_dict['bricks'] = self.bricks
            self.create_yaml_dict('bricks', self.section_dict['bricks'], False)
            self.device_count = len(self.bricks)
            if 'pvcreate.yml' not in Global.playbooks:
                Global.playbooks.append('pvcreate.yml')
            return True
        else:
            return False

    def write_vg_names(self):
        if not self.write_brick_names():
            return False
        vgs = self.section_data_gen('vgs', 'Volume Groups')
        if vgs:
            self.create_yaml_dict('vgs', vgs, False)
            self.section_dict['vgs'] = vgs
            data = []
            for i, j in zip(self.section_dict['bricks'], vgs):
                vgnames = {}
                vgnames['brick'] = i
                vgnames['vg'] = j
                data.append(vgnames)
            self.create_yaml_dict('vgnames', data, True)
            if 'vgcreate.yml' not in Global.playbooks:
                Global.playbooks.append('vgcreate.yml')
            return True
        return False


    def write_lv_names(self):
        if not self.write_pool_names():
            return False
        lvs = self.section_data_gen('lvs', 'Logical Volumes')
        if lvs:
            self.section_dict['lvs'] = lvs
            data = []
            for i, j, k in zip(self.section_dict['pools'],
                    self.section_dict['vgs'], lvs):
                pools = {}
                pools['pool'] = i
                pools['vg'] = j
                pools['lv'] = k
                data.append(pools)
            self.create_yaml_dict('lvpools', data, True)
            if 'lvcreate.yml' not in Global.playbooks:
                Global.playbooks.append('lvcreate.yml')
            return True
        return False

    def write_pool_names(self):
        if not self.write_vg_names():
            return False
        pools = self.section_data_gen('pools', 'Logical Pools')
        if pools:
            self.section_dict['pools'] = pools
            data = []
            for i, j in zip(pools, self.section_dict['vgs']):
                pools = {}
                pools['pool'] = i
                pools['vg'] = j
                data.append(pools)
            self.create_yaml_dict('pools', data, True)
            return True
        return False

    def write_lvol_names(self):
        if not self.write_lv_names():
            return False
        lvols = ['/dev/%s/%s' % (i, j) for i, j in
                                      zip(self.section_dict['vgs'],
                                          self.section_dict['lvs'])]
        if lvols:
            self.section_dict['lvols'] = lvols
            self.create_yaml_dict('lvols', lvols, False)
            if 'fscreate.yml' not in Global.playbooks:
                Global.playbooks.append('fscreate.yml')
            return True
        return False

    def write_mount_options(self):
        if not self.write_lvol_names():
            return False
        self.mountpoints = self.section_data_gen(
                'mountpoints', 'Mount Point')
        data = []
        self.section_dict['mountpoints'] = self.mountpoints
        for i, j in zip(self.mountpoints, self.section_dict['lvols']):
            mntpath = {}
            mntpath['path'] = i
            mntpath['device'] = j
            data.append(mntpath)
        self.create_yaml_dict('mntpath', data, True)
        self.modify_mountpoints()
        self.create_yaml_dict('mountpoints', self.mountpoints, False)
        if 'mount.yml' not in Global.playbooks:
            Global.playbooks.append('mount.yml')
        return True


    def modify_mountpoints(self):
        force = self.config_section_map(self.config, 'volume', 'force',
                False) or ''
        opts = self.get_options('brick_dirs')
        brick_dir, brick_list = [], []
        brick_dir = self.pattern_stripping(opts)

        if not opts:
            if force.lower() == 'no':
                msg = "Mountpoints cannot be brick directories.\n " \
                        "Provide 'brick_dirs' option/section or use force=yes"\
                        " in your configuration file. Exiting!"
                print "\nError: " + msg
                Global.logger.error(msg)
                self.cleanup_and_quit()
            elif force.lower() == 'yes':
                brick_list = self.mountpoints
            else:
                for mntpath in self.mountpoints:
                    if mntpath.endswith('/'):
                        mntpath = mntpath[:-1]
                    brick_list.append(self.get_file_dir_path(mntpath,
                                                     os.path.basename(mntpath)))

        else:
            if (len(brick_dir) != len(self.mountpoints
                                    ) and len(brick_dir) != 1):
                    msg = "The number of brick_dirs is different "\
                        "from that of " \
                        "the mountpoints available.\nEither give %d " \
                        "brick_dirs or provide a common one or leave this "\
                        "empty." % (len(self.mountpoints))
                    print "\nError:  " + msg
                    Global.logger.error(msg)
                    self.cleanup_and_quit()

            brick_dir = self.sub_directory_check(brick_dir)
            brick_list = [
                self.get_file_dir_path(
                    mntpath, brick) for mntpath, brick in zip(
                    self.mountpoints, brick_dir)]

        for brick, mountpoint in zip( brick_list, self.mountpoints):
            if brick == mountpoint:
                if force.lower() != 'yes':
                    msg = "Mount point cannot be brick.\nProvide a "\
                        "directory inside %s under the 'brick_dirs' " \
                        "option or provide option 'force=yes' under 'volume' " \
                        "section." % mountpoint
                    print "\nError: " + msg
                    Global.logger.error(msg)
                    self.cleanup_and_quit()
                else:
                    warn = "\nWarning: Using mountpoint itself as the brick in one or " \
                            "more hosts since force" \
                        " is specified, although not recommended.\n"
                    Global.logger.warning(warn)
                    if warn not in Global.warnings:
                        Global.warnings.append(warn)

        force = 'yes' if force.lower() == 'yes' else 'no'
        self.create_yaml_dict('force', force, False)
        self.mountpoints = brick_list


    def sub_directory_check(self, brick_dir):
        if len(brick_dir) == 1:
            brick_dir = brick_dir * len(self.mountpoints)
        for mnt, brick in zip(self.mountpoints, brick_dir):
            if brick.startswith('/'):
                if self.not_subdir(mnt, brick):
                    msg = "brick_dirs should be a directory " \
                        "inside mountpoint(%s).\nMake sure " \
                        "relative paths for all the %s mountpoints "\
                        "are given separately. "\
                        "Exiting!" %(mnt, len(self.mountpoints))
                    print "\nError: " + msg
                    Global.logger.error(msg)
                    self.cleanup_and_quit()
        return brick_dir

    def tune_profile(self):
        profile = self.get_options('tune-profile')
        profile = None if not profile else profile[0]
        if not profile:
            return
        self.create_yaml_dict('profile', profile, False)
        if 'tune-profile.yml' not in Global.playbooks:
            Global.playbooks.append('tune-profile.yml')



    def perf_spec_data_write(self):
        '''
        Now this one looks dirty. Couldn't help it.
        This one reads the performance related data like
        number of data disks and stripe unit size  if
        the option disk type is provided in the config.
        Some calculations are made as to enhance
        performance
        '''
        disktype = self.get_options('disktype')
        if disktype:
            perf = dict(disktype=disktype[0].lower())
            if perf['disktype'] not in ['raid10', 'raid6', 'jbod']:
                msg = "Unsupported disk type!"
                print "\nError: " + msg
                Global.logger.error(msg)
                self.cleanup_and_quit()
            if perf['disktype'] != 'jbod':
                diskcount = self.get_options('diskcount')
                if not diskcount:
                    print "Error: 'diskcount' not provided for " \
                    "disktype %s" % perf['disktype']
                perf['diskcount'] = int(diskcount[0])
                stripe_size = self.get_options('stripesize')
                if not stripe_size and perf['disktype'] == 'raid6':
                    print "Error: 'stripesize' not provided for " \
                    "disktype %s" % perf['disktype']
                if stripe_size:
                    perf['stripesize'] = int(stripe_size[0])
                    if perf['disktype'] == 'raid10' and perf[
                            'stripesize'] != 256:
                        warn = "Warning: We recommend a stripe unit size of 256KB " \
                            "for RAID 10"
                        Global.logger.warning(warn)
                        if warn not in Global.warnings:
                            Global.warnings.append(warn)
                else:
                    perf['stripesize'] = 256
                perf['dalign'] = {
                    'raid6': perf['stripesize'] * perf['diskcount'],
                    'raid10': perf['stripesize'] * perf['diskcount']
                }[perf['disktype']]
            else:
                perf['dalign'] = 256
                perf['diskcount'] = perf['stripesize'] = 0
        else:
            perf = dict(disktype='jbod')
            perf['dalign'] = 256
            perf['diskcount'] = perf['stripesize'] = 0
        self.iterate_dicts_and_yaml_write(perf)

    def insufficient_param_count(self, section, count):
        msg = "Please provide %s names for %s devices " \
            "else leave the field empty" % (section, count)
        print "Error: " + msg
        Global.logger.error(msg)
        self.cleanup_and_quit()

    def section_data_gen(self, section, section_name):
        opts = self.get_options(section)
        options = self.pattern_stripping(opts)
        if options:
            if len(options) != self.device_count:
                return self.insufficient_param_count(
                    section_name,
                    self.device_count)
        elif self.default:
            options = []
            pattern = {'vgs': 'GLUSTER_vg',
                       'pools': 'GLUSTER_pool',
                       'lvs': 'GLUSTER_lv',
                       'mountpoints': '/gluster/brick'
                       }[section]
            for i in range(1, self.device_count + 1):
                options.append(pattern + str(i))
        return options

