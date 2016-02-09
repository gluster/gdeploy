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

from gdeploylib import *
from gdeploylib.defaults import *
import sys
import re
try:
    import yaml
except ImportError:
    msg = "Package PyYAML not found."
    print "\nError: " + msg
    Global.logger.error(msg)
    sys.exit(0)
import os


class BackendSetup(Helpers):

    def __init__(self):
        self.section_dict = dict()
        self.previous = True
        self.write_sections()

    def write_sections(self):
        Global.logger.info("Reading configuration for backend setup")
        self.filename =  Global.group_file
        backend_setup, hosts = self.check_backend_setup_format()
        default = self.config_get_options('default', False)
        gluster = self.config_get_options('gluster', False)
        if default:
            self.default = False if default[0].lower() == 'no' else True
        self.default = self.default if hasattr(self, 'default') else True
        if gluster and gluster[0].lower() == 'no':
            self.gluster = False
            self.default = False
        else:
            self.gluster = True
        if not backend_setup:
            self.old_backend_setup()
        else:
            self.new_backend_setup(hosts)

    def call_selinux(self):
        selinux = self.config_get_options('selinux', False)
        if selinux:
            if selinux[0].lower() == 'yes':
                self.run_playbook(SELINUX_YML)


    def new_backend_setup(self, hosts):
        hosts = filter(None, hosts)
        if hosts:
            Global.var_file = None
            hosts = self.pattern_stripping(hosts)
            for host in hosts:
                self.bricks = []
                Global.current_hosts = [host]
                self.host_file = self.get_file_dir_path(Global.host_vars_dir, host)
                self.touch_file(self.host_file)
                self.parse_section(':' + host)
                self.call_gen_methods()
                self.remove_section(Global.inventory, Global.group)
                self.call_selinux()
        self.section_dict = None
        Global.var_file = None
        self.parse_section('')
        Global.current_hosts = [host for host in Global.hosts if host not in
                hosts]
        if self.section_dict:
            self.filename =  Global.group_file
            self.call_gen_methods()
            print self.section_dict, "yes!!!!"
            self.create_var_files(self.section_dict)
            self.remove_section(Global.inventory, Global.group)
            Global.var_file = 'group_vars'
            self.call_selinux()
        Global.hosts.extend(hosts)

    def old_backend_setup(self):
        if not self.get_var_file_type():
            return
        else:
            if Global.var_file == 'host_vars':
                for host in Global.hosts:
                    self.current_host = host
                    Global.current_hosts = [host]
                    devices = self.config_section_map(host,
                                              'devices', False)
                    self.filename = self.get_file_dir_path(Global.host_vars_dir, host)
                    self.touch_file(self.filename)
                    self.bricks = self.split_comma_separated_options(devices)
                    self.call_gen_methods()
                    self.call_selinux()
            else:
                Global.current_hosts = Global.hosts
                self.filename =  Global.group_file
                self.call_gen_methods()
                self.create_var_files(self.section_dict)
                self.remove_section(Global.inventory, Global.group)
                self.call_selinux()
            # msg = "This configuration format will be deprecated  "\
            # "in the next release.\nPlease refer the setup guide "\
            # "for the new configuration format."
            # print "Warning: " + msg
            # Global.logger.warning(msg=msg)

    def parse_section(self, hostname):
        try:
            self.section_dict = Global.sections['backend-setup' +
                    hostname]
            del self.section_dict['__name__']
        except KeyError:
            return
        try:
            self.filename = self.host_file
        except:
            self.filename =  Global.group_file
        self.section_dict = self.format_values(self.section_dict)

    def call_gen_methods(self):
        self.perf_spec_data_write()
        self.write_brick_names()
        self.write_vg_names()
        if self.gluster:
            self.write_thinp_names()
        else:
            self.write_lv_names()
        self.write_lvol_names()
        self.write_mount_options()
        self.write_brick_dirs()
        self.create_var_files(self.section_dict)


    def write_brick_names(self):
        self.bricks = self.section_data_gen('devices', 'Devices')
        ssd = filter(None, self.section_data_gen('ssd', "SSD"))
        if ssd:
            self.ssd = self.correct_brick_format(ssd)[0]
            self.section_dict['disk'] = self.ssd
            self.bricks.append(self.ssd)
        if not self.bricks:
            return
        self.bricks = self.correct_brick_format(self.bricks)
        self.device_count = len(self.bricks)
        self.section_dict['bricks'] = self.bricks
        if self.bricks:
            self.run_playbook(PVCREATE_YML)

    def write_vg_names(self):
        self.vgs = self.section_data_gen('vgs', 'Volume')
        if not self.vgs:
            if not self.bricks:
                return
            self.vgs = self.set_default('vgs')
        self.section_dict['vgs'] = self.vgs
        if not self.vgs:
            if not self.bricks:
                self.device_count = len(self.vgs)
            return
        data = []
        if self.device_count != len(self.section_dict['vgs']):
            if self.device_count > 1 and len(self.vgs) == 1:
                self.vgs *= self.device_count
                self.device_count = 1
            else:
                self.insufficient_param_count('vgs', self.device_count)
        for i, j in zip(self.bricks, self.vgs):
            vgnames = {}
            vgnames['brick'] = i
            vgnames['vg'] = j
            data.append(vgnames)
        self.section_dict['vgnames'] = filter(None, data)
        self.vgs = self.section_dict['vgs']
        if self.vgs:
            self.run_playbook(VGCREATE_YML)

    def write_thinp_names(self):
        self.pools = self.section_data_gen('pools', 'Logical Pools')
        if not self.pools:
            if not self.vgs:
                self.lvs = None
                return
            self.pools = self.set_default('pools')
        if not self.vgs:
            self.device_count = len(self.pools)
        self.lvs = self.section_data_gen('lvs', 'Logical Pools')
        if not self.lvs:
            self.lvs = self.set_default('lvs')
            if not self.lvs or not self.pools:
                return
        data = []
        if len(self.pools) != len(self.lvs):
                self.insufficient_param_count('lvs', len(self.pools))
        if self.device_count != len(self.pools):
            if self.device_count == 1:
                self.vgs *= len (self.pools)
            else:
                self.insufficient_param_count('pools', self.device_count)
        for i, j, k in zip(self.pools, self.vgs, self.lvs):
            pools = {}
            pools['pool'] = i
            pools['vg'] = j
            pools['lv'] = k
            data.append(pools)
        self.section_dict['lvpools'] = filter(None, data)
        if self.section_dict['lvpools']:
            self.run_playbook(GLUSTER_LV_YML)

    def write_lv_names(self):
        self.lvs = self.section_data_gen('lvs', 'Logical Volume')
        if not self.lvs:
            return
        self.section_dict['lvs'] = self.lvs
        for lv in self.lvs:
            self.lvs_with_size(lv, '100%FREE')
        datalv = self.section_data_gen('datalv', 'Data LV')
        if self.datalv[0] not in lvs:
            self.lvs.extend(self.datalv)
        #If SSD present for caching
        self.section_dict['vg'] = self.vgs[0]
        self.section_dict['force'] = self.config_get_options(Global.config,
                                               'force', False) or 'no'
        if hasattr(self, 'ssd'):
            if not hasattr(self, 'datalv'):
                print "\nError: Data lv('datalv' options) not specified for "\
                        "cache setup"
                return
            self.run_playbook(VGEXTEND_YML)
            self.section_dict['datalv'] = self.datalv[0]
            cachemeta = self.get_options(
                    'cachemetalv') or 'lv_cachemeta'
            cachedata = self.get_options(
                    'cachedatalv') or 'lv_cachedata'
            self.section_dict['cachemeta'] = self.lvs_with_size(cachemeta, '1024')
            self.section_dict['cachedata'] = self.lvs_with_size(cachedata, '4096')
        if not self.data:
            return
        self.section_dict['lvs'] = self.data
        self.run_playbook(LVCREATE_YML)
        if hasattr(self, 'ssd'):
            self.run_playbook(LVCONVERT_YML)


    def lvs_with_size(self, lv, d_size):
        name = lv.split(':')[0]
        try:
            size = lv.split(':')[1]
        except:
            size = d_size
        lvs = {}
        lvs['name'] = name
        lvs['size'] = size
        self.data.append(lvs)
        return lvs


    def write_lvol_names(self):
        if not (self.lvs and self.vgs):
            return
        lvols = ['/dev/%s/%s' % (i, j.split(':')[0]) for i, j in
                                      zip(self.vgs, self.lvs)]
        self.section_dict['lvols'] = lvols
        if self.section_dict['lvols']:
            self.run_playbook(FSCREATE_YML)

    def write_mount_options(self):
        if not self.section_dict.get('lvols'):
            return
        self.mountpoints = self.section_data_gen(
                'mountpoints', 'Mount Point')
        if not self.mountpoints:
            self.mountpoints = self.set_default('mountpoints')
        data = []
        self.section_dict['mountpoints'] = self.mountpoints
        if not self.mountpoints:
            return
        for i, j in zip(self.mountpoints, self.section_dict['lvols']):
            mntpath = {}
            mntpath['path'] = i
            mntpath['device'] = j
            data.append(mntpath)
        self.section_dict['mntpath'] = filter(None, data)
        if self.section_dict['mntpath']:
            self.run_playbook(MOUNT_YML)

    def write_brick_dirs(self):
        force = self.config_section_map('volume',
                'force', False) or ''
        brick_dirs = []
        brick_dirs = self.section_data_gen('brick_dirs', 'Brick directories')
        if not brick_dirs:
            if force.lower() == 'no':
                print "Error: Mount points cannot be brick directories.\n" \
                        "Provide 'brick_dirs' option/section or use force=yes"\
                        " in your configuration file. Exiting!"
                return
            else:
                if not hasattr(self, 'mountpoints'):
                    return
                if force.lower() == 'yes':
                    brick_dirs = self.mountpoints
                else:
                    if not hasattr(self, 'mountpoints'):
                        return
                    for mntpath in self.mountpoints:
                        if mntpath.endswith('/'):
                            mntpath = mntpath[:-1]
                        brick_dirs.append(self.get_file_dir_path(mntpath,
                                                         os.path.basename(mntpath)))
            brick_list = brick_dirs
        else:
            if (len(brick_dirs) != len(self.mountpoints
                                    ) and len(brick_dirs) != 1):
                    msg = "The number of brick_dirs is different "\
                        "from that of " \
                        "the mountpoints available.\nEither give %d " \
                        "brick_dirs or provide a common one or leave this "\
                        "empty." % (len(self.mountpoints))
                    return
            brick_dir = self.sub_directory_check(brick_dirs)
            brick_list = []
            brick_list = [
                self.get_file_dir_path(
                    mntpath, brick) for mntpath, brick in zip(
                    self.mountpoints, brick_dir)]
            for brick, mountpoint in zip( brick_list, self.mountpoints):
                if brick == mountpoint:
                    if force.lower() != 'yes':
                        msg = "Error: Mount point cannot be brick.\nProvide a "\
                            "directory inside %s under the 'brick_dirs' " \
                            "option or provide option 'force=yes' under 'volume' " \
                            "section." % mountpoint
                        return
                    else:
                        print "\nWarning: Using mountpoint itself as the brick in one or " \
                                "more hosts since force" \
                            " is specified, although not recommended.\n"

        force = 'yes' if force.lower() == 'yes' else 'no'
        self.section_dict['force'] = force
        if hasattr(self, 'host_file'):
            self.filename = self.host_file
            self.section_dict['mountpoints'] = brick_list
            self.create_var_files(self.section_dict)
        else:
            if self.section_dict.get('mountpoints'):
                self.section_dict['mountpoints'].extend(brick_list)
            else:
                self.section_dict['mountpoints'] = bricklist
        return


    def correct_brick_format(self, brick_list):
        bricks = []
        for brick in brick_list:
            if not brick.startswith('/dev/'):
                bricks.append('/dev/' + brick)
            else:
                bricks.append(brick)
        return bricks

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
        self.create_var_files(perf, False, Global.group_file)

    def insufficient_param_count(self, section, count):
        msg = "Please provide %s names for %s devices " \
            "else leave the field empty" % (section, count)
        print "Error: " + msg
        Global.logger.error(msg)
        self.cleanup_and_quit()

    def section_data_gen(self, section, section_name):
        opts = self.get_options(section)
        options = self.pattern_stripping(opts)
        return filter(None, self.listify(options))

    def set_default(self, section):
        if not self.default:
            return
        options = []
        pattern = BSETUP_DEFAULTS[section]
        for i in range(1, self.device_count + 1):
            options.append(pattern + str(i))
        return options
