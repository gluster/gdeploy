#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    YamlWriter is a helper class used by VarFileGenerator to write
#    all the necessary sections and options into the yaml file
#    as per specified in the configuration file
#
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

import yaml
from conf_parser import ConfigParseHelpers


class YamlWriter(ConfigParseHelpers):

    def __init__(self, bricks, config, filename, filetype):
        self.bricks = bricks
        self.config = config
        self.filename = filename
        self.filetype = filetype
        self.device_count = len(bricks)
        self.mountpoints = self.section_data_gen('mountpoints', 'Mount Point')
        self.write_sections()

    def write_sections(self):
        if self.bricks:
            ConfigParseHelpers.setup_backend = True
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
            listables_in_yaml = {key: self.section_dict[key]
                    for key in ['vgs', 'bricks', 'mountpoints', 'lvols'] }
            self.yaml_list_data_write(listables_in_yaml)
            self.yaml_dict_data_write()
            self.perf_spec_data_write()
        elif self.mountpoints:
            ConfigParseHelpers.setup_backend = False
            print "Warning: Since no brick data is provided, we cannot do a "\
                    "backend setup. Continuing with gluster deployement using "\
                    " the mount points %s" % ', '.join(self.mountpoints)
            self.yaml_list_data_write({'mountpoints': self.mountpoints})
        else:
            print "Error: Device names for backend setup or mount point " \
                    "details for gluster deployement not provided. Exiting."
            sys.exit(0)
        self.gluster_vol_spec()

    def insufficient_param_count(self, section, count):
        print "Error: Please provide %s names for %s devices " \
            "else leave the field empty" % (section, count)
        sys.exit(0)

    def split_comma_seperated_options(self, options):
        if options:
            return filter(None, options.split(','))
        return []

    def get_options(self, section, required):
        if self.filetype == 'group_vars':
            return self.config_get_options(self.config, section, required)
        else:
            return self.split_comma_seperated_options(
                    self.config_section_map(
                self.config, self.filename.split('/')[-1], section,
                required))

    def section_data_gen(self, section, section_name):
        options = self.get_options(section, False)
        if options:
            if len(options) < self.device_count:
                return self.insufficient_param_count(
                    section_name,
                    self.device_count)
        else:
            pattern = {'vgs': 'RHS_vg',
                       'pools': 'RHS_pool',
                       'lvs': 'RHS_lv',
                       'mountpoints': '/rhs/brick'
                       }[section]
            for i in range(1, self.device_count + 1):
                options.append(pattern + str(i))
        return options

    def yaml_list_data_write(self, data_dict):
        for key, value in data_dict.iteritems():
            data = {}
            data[key] = value
            self.write_yaml(data, False)

    def create_yaml_dict(self, section, data):
        data_dict = {}
        data_dict[section] = data
        self.write_yaml(data_dict, True)

    def yaml_dict_data_write(self):
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
        for key, value in data_dict.iteritems():
            self.create_yaml_dict(key, value)

    def gluster_vol_spec(self):
        clients=self.config_section_map(self.config, 'clients', 'hosts',
                False)
        if not clients:
            print "Client hosts are not specified. Skipping GlusterFS " \
                    "deploy configuration details."
            ConfigParseHelpers.gluster_ret = False
            return
        gluster = dict(clients=self.split_comma_seperated_options(clients))
        client_mntpts = self.config_section_map(
                self.config, 'clients', 'mount_points',
                False) or '/mnt/gluster'
        if client_mntpts:
            gluster['client_mount_points'] = self.split_comma_seperated_options(
                                                            client_mntpts)
            if len(gluster['client_mount_points']) != len(
                    gluster['clients']) or len(
                            gluster['client_mount_points']) != 1:
                print "Error: Provide volume mount points in each client " \
                        "or a common mount point for all the clients. "
                sys.exit(0)
        gluster['volname'] = self.config_get_options(self.config,
                'volname', False) or 'vol1'
        self.yaml_list_data_write(gluster)
        ConfigParseHelpers.gluster_ret = True

    def perf_spec_data_write(self):
        disktype = self.config_get_options(self.config,
                                           'disktype', False)
        if disktype:
            perf = dict(disktype=disktype[0].lower())
            if perf['disktype'] not in ['raid10', 'raid6', 'jbod']:
                print "Error: Unsupported disk type!"
                sys.exit(0)
            if perf['disktype'] != 'jbod':
                perf['diskcount'] = int(
                    self.config_get_options(self.config, 'diskcount', True)[0])
                stripe_size_necessary = {'raid10': False,
                                         'raid6': True
                                        }[perf['disktype']]
                stripe_size = self.config_get_options(self.config, 'stripesize',
                    stripe_size_necessary)
                if stripe_size:
                    perf['stripesize'] = int(stripe_size[0])
                    if perf['disktype'] == 'raid10' and perf['stripesize'] != 256:
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
        perf['profile'] = self.config_get_options(self.config,
                'tune-profile', False) or 'rhs-high-throughput'
        self.yaml_list_data_write(perf)

    def write_yaml(self, data_dict, data_flow):
        with open(self.filename, 'a+') as outfile:
            if not data_flow:
                outfile.write(
                    yaml.dump(
                        data_dict,
                        default_flow_style=data_flow))
            else:
                outfile.write(yaml.dump(data_dict))
