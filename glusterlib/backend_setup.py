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
try:
    import yaml
except ImportError:
    print "Error: Package PyYAML not found."
    sys.exit(0)
import os


class BackendSetup(YamlWriter):

    def __init__(self, bricks, config, filename, filetype):
        self.config = config
        self.filename = filename
        self.filetype = filetype
        self.bricks = bricks
        self.device_count = len(bricks)
        self.write_sections()

    def write_sections(self):
        self.write_brick_names()
        self.write_vg_names()
        self.write_pool_names()
        self.write_lv_names()
        self.write_lvol_names()
        self.write_mount_options()
        self.perf_spec_data_write()
        self.tune_profile()
        return True

    def write_brick_names(self):
        self.create_yaml_dict('bricks', self.bricks, False)
        if 'pvcreate.yml' not in Global.playbooks:
            Global.playbooks.append('pvcreate.yml')

    def write_vg_names(self):
        self.vgs = self.section_data_gen(self.config, 'vgs', 'Volume Groups')
        if self.vgs:
            self.create_yaml_dict('vgs', self.vgs, False)
            data = []
            for i, j in zip(self.bricks, self.vgs):
                vgnames = {}
                vgnames['brick'] = i
                vgnames['vg'] = j
                data.append(vgnames)
            self.create_yaml_dict('vgnames', data, True)
            if 'vgcreate.yml' not in Global.playbooks:
                Global.playbooks.append('vgcreate.yml')


    def write_lv_names(self):
        self.lvs = self.section_data_gen(self.config, 'lvs', 'Logical Volumes')
        if self.lvs:
            data = []
            for i, j, k in zip(self.pools, self.vgs, self.lvs):
                pools = {}
                pools['pool'] = i
                pools['vg'] = j
                pools['lv'] = k
                data.append(pools)
            self.create_yaml_dict('lvpools', data, True)
            if 'lvcreate.yml' not in Global.playbooks:
                Global.playbooks.append('lvcreate.yml')

    def write_pool_names(self):
        self.pools = self.section_data_gen(self.config, 'pools', 'Logical Pools')
        if self.pools:
            data = []
            for i, j in zip(self.pools, self.vgs):
                pools = {}
                pools['pool'] = i
                pools['vg'] = j
                data.append(pools)
            self.create_yaml_dict('pools', data, True)

    def write_lvol_names(self):
        self.lvols = ['/dev/%s/%s' % (i, j) for i, j in
                                      zip(self.vgs, self.lvs)]
        if self.lvols:
            self.create_yaml_dict('lvols', self.lvols, False)
            if 'fscreate.yml' not in Global.playbooks:
                Global.playbooks.append('fscreate.yml')

    def write_mount_options(self):
        self.mountpoints = self.section_data_gen(self.config,
                'mountpoints', 'Mount Point')
        data = []
        for i, j in zip(self.mountpoints, self.lvols):
            mntpath = {}
            mntpath['path'] = i
            mntpath['device'] = j
            data.append(mntpath)
        self.create_yaml_dict('mntpath', data, True)
        self.modify_mountpoints()
        self.create_yaml_dict('mountpoints', self.mountpoints, False)
        if 'mount.yml' not in Global.playbooks:
            Global.playbooks.append('mount.yml')


    def modify_mountpoints(self):
        force = self.config_section_map(self.config, 'volume', 'force', False)
        if (force and force.lower() == 'yes'):
            return
        opts = self.get_options(self.config, 'brick_dirs', False)
        brick_dir, brick_list = [], []
        brick_dir = self.pattern_stripping(opts)

        if not opts:
            if (force and force.lower() == 'no'):
                print "\nError: Mountpoints cannot be brick directories.\n " \
                        "Provide 'brick_dirs' option/section or use force=yes"\
                        " in your configuration file. Exiting!"
                self.cleanup_and_quit()
            for mntpath in self.mountpoints:
                if mntpath.endswith('/'):
                    mntpath = mntpath[:-1]
                brick_list.append(self.get_file_dir_path(mntpath,
                                                 os.path.basename(mntpath)))

        else:
            if (len(brick_dir) != len(self.mountpoints
                                    ) and len(brick_dir) != 1):
                    print "\nError: The number of brick_dirs is different "\
                        "from that of " \
                        "the mountpoints available.\nEither give %d " \
                        "brick_dirs or provide a common one or leave this "\
                        "empty." % (len(self.mountpoints))
                    self.cleanup_and_quit()

            for sub, mnt in zip(brick_dir, self.mountpoints):
                if sub.startswith('/'):
                    if self.not_subdir(mnt, sub):
                        print "\nError: brick_dirs should be a directory " \
                            "inside mountpoint(%s).\nProvide absolute" \
                            " path of a directory inside %s or just give the"\
                            " path relative to it. " \
                            "Exiting!" %(mnt, mnt)
                        self.cleanup_and_quit()
                    brick_list = brick_dir

            if not brick_list:
                if len(brick_dir) != 1:
                    brick_list = [
                        self.get_file_dir_path(
                            mntpath,
                            brick_dir[0]) for mntpath in self.mountpoints]
                else:
                    brick_list = [
                        self.get_file_dir_path(
                            mntpath, brick) for mntpath, brick in zip(
                            self.mountpoints, brick_dir)]

        for brick, mountpoint in zip( brick_list, self.mountpoints):
            if brick == mountpoint:
                print "\nError: Mount point cannot be brick.\nProvide a "\
                    "directory inside %s under the 'brick_dirs' " \
                    "option or provide option 'force=yes' under 'volume' " \
                    "section." % mountpoint
                self.cleanup_and_quit()
        self.mountpoints = brick_list

    def tune_profile(self):
        profile = self.config_get_options(self.config, 'tune-profile', False)
        profile = 'rhs-high-throughput' if not profile else profile[0]
        if profile.lower() == 'none':
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
        disktype = self.config_get_options(self.config,
                                           'disktype', False)
        if disktype:
            perf = dict(disktype=disktype[0].lower())
            if perf['disktype'] not in ['raid10', 'raid6', 'jbod']:
                print "Error: Unsupported disk type!"
                self.cleanup_and_quit()
            if perf['disktype'] != 'jbod':
                perf['diskcount'] = int(self.get_options(self.config,
                    'diskcount', True)[0])
                stripe_size_necessary = {'raid10': False,
                                         'raid6': True
                                         }[perf['disktype']]
                stripe_size = self.get_options(self.config, 'stripesize',
                                               stripe_size_necessary)
                if stripe_size:
                    perf['stripesize'] = int(stripe_size[0])
                    if perf['disktype'] == 'raid10' and perf[
                            'stripesize'] != 256:
                        print "Warning: We recommend a stripe unit size of 256KB " \
                            "for RAID 10"
                else:
                    perf['stripesize'] = 256
                perf['dalign'] = {
                    'raid6': perf['stripesize'] * perf['diskcount'],
                    'raid10': perf['stripesize'] * perf['diskcount']
                }[perf['disktype']]
        else:
            perf = dict(disktype='jbod')
            perf['dalign'] = 256
            perf['diskcount'] = perf['stripesize'] = 0
        self.iterate_dicts_and_yaml_write(perf)

    def insufficient_param_count(self, section, count):
        print "Error: Please provide %s names for %s devices " \
            "else leave the field empty" % (section, count)
        self.cleanup_and_quit()

    def section_data_gen(self, config, section, section_name):
        opts = self.get_options(config, section, False)
        options = []
        for option in opts:
            options += self.parse_patterns(option)
        if options:
            if len(options) < self.device_count:
                return self.insufficient_param_count(
                    section_name,
                    self.device_count)
        else:
            pattern = {'vgs': 'GLUSTER_vg',
                       'pools': 'GLUSTER_pool',
                       'lvs': 'GLUSTER_lv',
                       'mountpoints': '/gluster/brick'
                       }[section]
            for i in range(1, self.device_count + 1):
                options.append(pattern + str(i))
        return options

