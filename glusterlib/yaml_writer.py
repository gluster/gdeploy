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
try:
    import yaml
except ImportError:
    print "Error: Package PyYAML not found."
    sys.exit(0)
import os


class YamlWriter(ConfigParseHelpers):

    def __init__(self, bricks, config, filename, filetype):
        self.config = config
        self.filename = filename
        self.filetype = filetype
        self.bricks = bricks
        self.device_count = len(bricks)
        self.mountpoints = self.section_data_gen('mountpoints', 'Mount Point')
        self.write_sections()

    def write_sections(self):
        '''
        device names, vg names, lv names, pool names, mount point,
        everything is read into a dictionary section_dict, so the association
        can be maintained between all these things. Association as in,
        /dev/vgname1/lvname1 is to be mounted at mount_point1 etc
        '''
        sections = ['vgs', 'lvs', 'pools']
        section_names = ['Volume Group', 'Logical Volume',
                         'Logical Pool']
        self.section_dict = {'bricks': self.bricks,
                             'mountpoints': self.mountpoints}
        for section, section_name in zip(sections, section_names):
            self.section_dict[section] = self.section_data_gen(
                section,
                section_name)
        self.section_dict['lvols'] = ['/dev/%s/%s' % (i, j) for i, j in
                                      zip(self.section_dict['vgs'],
                                          self.section_dict['lvs'])]
        self.yaml_dict_data_write()
        self.modify_mountpoints()
        listables_in_yaml = {}
        for key in [ 'vgs', 'bricks', 'mountpoints', 'lvols']:
            listables_in_yaml[key] = self.section_dict[key]
        self.iterate_dicts_and_yaml_write(listables_in_yaml)
        self.perf_spec_data_write()
        return True

    def insufficient_param_count(self, section, count):
        print "Error: Please provide %s names for %s devices " \
            "else leave the field empty" % (section, count)
        self.cleanup_and_quit()

    def split_comma_seperated_options(self, options):
        if options:
            return filter(None, options.split(','))
        return []

    def get_options(self, section, required):
        if self.filetype == 'group_vars':
            return self.config_get_options(self.config, section, required)
        else:
            options = self.config_section_map(
                self.config, self.filename.split('/')[-1], section, required)
            return self.split_comma_seperated_options(options)

    def modify_mountpoints(self):
        opts = self.get_options('brick_dir', False)
        brick_dir = []
        for option in opts:
            brick_dir += self.parse_patterns(option)
        if len(brick_dir) == 1:
            brick_dir = brick_dir[0]

        if not brick_dir:
            force = self.config_section_map(self.config, 'volume', 'force', False)
            if force == 'yes':
                return
            brick_list = [self.get_file_dir_path(mntpath,
                                                 os.path.basename(mntpath)) for
                          mntpath in self.section_dict['mountpoints']]

        else:
            if True in [brick.startswith('/') for brick in brick_dir]:
                print "Error: brick_dir should be relative to the " \
                    "mountpoint. Looks like you have provided an " \
                    "absolute path. "
                self.cleanup_and_quit()

            if isinstance(brick_dir, list):
                if len(brick_dir) != len(self.section_dict['mountpoints']):
                    if len(brick_dir) != 1:
                        print "Error: The brick_dir length does not match with "\
                            "the mountpoints available. Either give %d number " \
                            "of brick_dir, provide a common one or leave this "\
                            "empty." % (len(self.section_dict['mountpoints']))
                        self.cleanup_and_quit()
                    else:
                        brick_list = [
                            self.get_file_dir_path(
                                mntpath,
                                brick_dir[0]) for mntpath in self.section_dict['mountpoints']]
                else:
                    brick_list = [
                        self.get_file_dir_path(
                            mntpath, brick) for mntpath, brick in zip(
                            self.section_dict['mountpoints'], brick_dir)]
        for brick, mountpoint in zip(
                brick_list, self.section_dict['mountpoints']):
            if brick == mountpoint and not force:
                print "Error: Mount point cannot be brick. Provide 'brick_dir' " \
                    "option or provide option 'force=True' under 'volume' " \
                    "section."
                self.cleanup_and_quit()
        self.section_dict['mountpoints'] = brick_list

    def section_data_gen(self, section, section_name):
        opts = self.get_options(section, False)
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

    def iterate_dicts_and_yaml_write(self, data_dict, keep_format=False):
        # Just a pretty wrapper over create_yaml_dict to iterate over dicts
        for key, value in data_dict.iteritems():
            if key not in ['__name__']:
                self.create_yaml_dict(key, value, keep_format)

    def create_yaml_dict(self, section, data, keep_format=True):
        '''
        This method is called if in the playbook yaml,
        the options are to be written as a list
        '''
        data_dict = {}
        data_dict[section] = data
        self.write_yaml(data_dict, keep_format)

    def yaml_dict_data_write(self):
        '''
        Matter complicates when the data are to be written as a dictionary
        in the yaml. for the data with above mentioned associations are
        to be written as a dictionary itself in the yaml, the dictionary
        section_dict is iterated keeping the associations intact, and
        multiple lists are created for vgs, lvs, pools, mountpoints
        '''
        # Just a pretty way to initialise 4 empty lists
        vgnames, mntpaths, lvpools, pools = ([] for i in range(4))
        for i, vg in enumerate(self.section_dict['vgs']):
            vgnames.append({'brick': self.section_dict['bricks'][i], 'vg': vg})
            mntpaths.append({'path': self.section_dict['mountpoints'][i],
                             'device': self.section_dict['lvols'][i]})
            lvpools.append({'pool': self.section_dict['pools'][i], 'vg': vg,
                            'lv': self.section_dict['lvs'][i]})
            pools.append({'pool': self.section_dict['pools'][i], 'vg': vg})
        data_dict = {
            'vgnames': vgnames,
            'lvpools': lvpools,
            'mntpath': mntpaths,
            'pools': pools}
        self.iterate_dicts_and_yaml_write(data_dict, True)

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
                perf['diskcount'] = int(self.get_options('diskcount', True)[0])
                stripe_size_necessary = {'raid10': False,
                                         'raid6': True
                                         }[perf['disktype']]
                stripe_size = self.get_options('stripesize',
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
        perf['profile'] = self.config_get_options(
            self.config,
            'tune-profile',
            False) or 'rhs-high-throughput'
        self.iterate_dicts_and_yaml_write(perf)

    def write_yaml(self, data_dict, data_flow):
        with open(self.filename, 'a+') as outfile:
            if not data_flow:
                outfile.write(
                    yaml.dump(
                        data_dict,
                        default_flow_style=data_flow))
            else:
                outfile.write(yaml.dump(data_dict))
