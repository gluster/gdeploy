#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Ansible module to create or remove a Volume Group.
(c) 2015 Nandaja Varma <nvarma@redhat.com>, Ashmitha Ambastha <asambast@redhat.com>
This file is part of Ansible
Ansible is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Ansible is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Ansible. If not, see <http://www.gnu.org/licenses/>.
"""

DOCUMENTATION = '''
---
author: Nandaja Varma , Ashmitha Ambastha
module: vg
short_description: Create, extend, reduce, convert, and remove a Volume Group.
description:
    - Creates, extends, reduces, converts, and removes a Volume Group.
options:
    action:
        required: true
        choices: [create,  extend, reduce, convert, remove]
        description: Specifies the vg operation that is to be executed on the vg
    disk:
        required: true
        description: Physical Volumes on which the Volume Groups are to be
                     created or Volume Groups that are to be removed needs to
                     be specified here.
    vgname:
        required: true
        description: Names of the Volume Group
    disk_type:
        required: false
        choices: [raid10, raid6, jbod]
        description: Specifies which disk configuration is used while
                     setting up the backend.
    stripe_size:
        required: false
        description: Specifies the stripe unit size of each disk
                     in the architecture
    diskcount:
        required: false
        description: Specifies the number of data disk in the
                     configuration.
    force:
        required: false
        description: Force  the  creation  without  any confirmation.
    uuid:
        required: false
        description: Specify the uuid for the device.  Without this option,
                     pvcreate generates a random uuid.
    zero:
        required: false
        description: Whether or not the first 4 sectors of the device should
                     be wiped.
    metadatasize:
        required: false
        description: The approximate amount of space to be set aside for
                     each metadata area.
    dataalignment:
        required: true
        description: Align the start of the data to a multiple of this number.


'''

EXAMPLES = '''
#Create Volume Groups on PVS /dev/vdb1
    - vg: action=create disk='["/dev/vdb"]'

#Remove Volume Groups RHS_vg1, RHS_vg2 and RHS_vg3
    - pv: action=remove
          vgname='["RHS_vg1", "RHS_vg2", "RHS_vg3"]'
'''

from ansible.module_utils.basic import *
from ast import literal_eval
import sys
import os


class VgOps(object):

    def __init__(self, module):
        self.module = module
        self.action = self.validated_params('action')
        self.op = 'vg' + self.action
        self.vgname = self.validated_params('vgname')
        self.disk = self.module.params['disk']

    def vg_actions(self):
        self.disk = self.module.params['disk']
        if not self.disk:
            self.disk = self.module.params['disks']
            print('disks paramater is deprecated, please use disk')
        return self.get_volume_command(self.disk)

    def get_volume_command(self, disk):
        args = ' ' + str()
        if not self.vgname:
            self.module.exit_json(rc=1, msg="Nothing to be done")
        elif self.action == 'create':
            if not self.disk:
                self.module.exit_json(rc=1, msg="Nothing to be done")
            self.disktype = self.module.params['disktype']
            if self.disktype and self.disktype not in ['jbod']:
                self.options += ' -s %sK ' % self._compute_size()
            args += " %s %s" % (self.vgname, self.disk)
            maxlogicalvolumes=self.module.params['maxlogicalvolumes']
            if maxlogicalvolumes:
                args += " -l " + maxlogicalvolumes
            maxphysicalvolumes= self.module.params['maxphysicalvolumes']
            if maxphysicalvolumes:
                args += " -p " + maxphysicalvolumes
            physicalextentsize=self.module.params['physicalextentsize']
            if physicalextentsize:
                args += " -s " + physicalextentsize
            zero = self.module.params['zero']
            if zero:
                args += " -Z y "
            metadatasize = self.module.params['metadatasize']
            if metadatasize:
                args += " --metadatasize " + metadatasize
            dataalignment = self.module.params['dataalignment']
            if dataalignment:
                args += " --dataalignment " + dataalignment
            dataalignmentoffset = self.module.params['dataalignmentoffset']
            if dataalignmentoffset:
                args += " --dataalignmentoffset " + dataalignmentoffset
        elif self.action == 'remove':
            args = " -y -ff " + self.vgname
        elif self.action == 'extend':
            if not hasattr(self, 'disk'):
                self.disk = self.validated_params('disk')
            args = " %s %s" % (self.vgname, self.disk)
            zero = self.module.params['zero']
            if zero:
                args += " -Z y "
            metadatasize = self.module.params['metadatasize']
            if metadatasize:
                args += " --metadatasize " + metadatasize
            metadataignore = self.module.params['metadataignore']
            if metadataignore == 'y':
                args += " --metadataignore " + metadataignore
            dataalignment = self.module.params['dataalignment']
            if dataalignment:
                args += " --dataalignment " + dataalignment
            dataalignmentoffset = self.module.params['dataalignmentoffset']
            if dataalignmentoffset:
                args += " --dataalignmentoffset " + dataalignmentoffset
        elif self.action == 'reduce':
            if not hasattr(self, 'disk'):
                self.disk = self.validated_params('disk')
            args = " %s %s" % (self.vgname, self.disk)
            removemissing =self.module.params['removemissing']
            if removemissing:
                args += "--removemissing"
        elif self.action == 'convert':
            args += " %s "%(self.vgname)
            metadatatype= self.module.params['metadatatype']
            if metadatatype:
                args+= " -M"+ metadatatype
            # self.module.exit_json(rc=1, msg=args)
        else:
            self.module.fail_json(rc=1, msg="Unknown action")
        return args

    def validated_params(self, opt):
        value = self.module.params[opt]
        if value is None:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(rc=1, msg=msg)
        return value

    def _compute_size(self):
        self.stripe_unit_size = self.validated_params('stripesize')
        self.diskcount = self.validated_params('diskcount')
        pe_size = int(self.stripe_unit_size) * int(self.diskcount)
        return pe_size

    def get_output(self, rc, output, err):
        if not rc:
            self.module.exit_json(rc=rc, stdout=output, changed=1)
        else:
            self.module.fail_json(rc=rc, msg=err)

    def vg_presence_check(self, vg):
        rc, out, err = self.run_command('vgdisplay', ' ' + vg)
        if self.action == 'create' and not rc:
            # volume group exists, exit!
            self.module.exit_json(changed=False, rc=1,
                                  msg="A volume group called %s already exists"
                                  %vg)
        elif self.action == 'extend' and rc:
            # volume group does not exist, exit!
            self.module.exit_json(changed=False, rc=1,
                                  msg="A volume group %s not found."%vg)
        elif self.action == 'reduce' and rc:
            # volume group does not exist, exit!
            self.module.exit_json(changed=False, rc=1,
                                  msg="A volume group %s not found."%vg)
        elif self.action == 'convert' and rc:
            # volume group does not exist, exit!
            self.module.exit_json(changed=False, rc=1,
                                  msg="A volume group %s not found."%vg)
        elif self.action == 'remove' and rc:
            self.module.exit_json(changed=False, rc=1,
                                  msg="Volume group %s not found"%vg)


    def pv_presence_check(self, disk):
        if self.action not in ['create', 'extend']:
            return 1
        rc, out, err = self.run_command('pvdisplay', ' ' + disk)
        if rc:
            dalign = self.module.params['dalign'] or ''
            opts = " --dataalignment %sk" % dalign if dalign else ''
            rc, out, err = self.run_command('pvcreate', opts +
                    ' ' + disk)
            if rc:
                self.module.fail_json(msg="Could not create PV", rc=rc)
        return 1

    def run_command(self, op, opts):
        cmd = self.module.get_bin_path(op, True) + opts
        return self.module.run_command(cmd)

if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(choices=["create", "remove", "extend", "reduce", "convert"], required=True),
            vgname=dict(type='str'),
            disks=dict(),
            disk=dict(),
            force=dict(type='str'),
            zero=dict(type='str'),
            maxlogicalvolumes=dict(type='str'),
            maxphysicalvolumes=dict(type='str'),
            physicalextentsize=dict(type='str'),
            metadatasize=dict(type='str'),
            dataalignment=dict(type='str'),
            dataalignmentoffset=dict(type='str'),
            metadataignore=dict(type='str'),
            diskcount=dict(),
            disktype=dict(),
            stripesize=dict(),
            metadatatype=dict(type='str'),
            removemissing=dict(type='str'),
        ),
    )

    vgops = VgOps(module)
    vgops.vg_presence_check(vgops.vgname)
    opts = vgops.vg_actions()
    vgops.pv_presence_check(vgops.disk)
    rc, out, err = vgops.run_command(vgops.op, opts)
    vgops.get_output(rc, out, err)
