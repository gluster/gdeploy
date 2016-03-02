#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Ansible module to create or remove a Volume Group.
(c) 2015 Nandaja Varma <nvarma@redhat.com>, Anusha Rao <aroa@redhat.com>
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
module: vg
short_description: Create or remove a Volume Group.
description:
    - Creates or removes n-number of Volume Groups on n-number
      of remote hosts

options:
    action:
        required: true
        choices: [create, remove]
        description: Specifies the vg operation that is to be executed,
                     either a volume group creation or deletion.
    disks:
        required: true
        description: Physical Volumes on which the Volume Groups are to be
                     created or Volume Groups that are to be removed needs to
                     be specified here.
    options:
        required: false
        description: Extra options that needs to be passed while creating the
                     Volume Groups can be given here. Check the man page of
                     vgcreate for more info.
    vg_pattern:
        required: true for create action
        description: The pattern to be followed while naming the volume
                     groups which are to be created. Pattern followed by
                     the ordinance of the volume group created will be
                     the name of that particulat volume group.
    vg_name:
        required: true for remove action
        description: Names of the Volume Groups that are to be removed

    disk_type:
        required: false
        choices: [raid10, raid6, jbod]
        description: Specifies which disk configuration is used while
        setting up the backend. Supports RAID 10, RAID 6 and JBOD
        configurations. Defining this will set the module to
        assign physicalextentsize best for the performance based
        on the number of datadisks and the stripe unit size in the
        configuration.

    stripe_size:
        required: true if disk_type is provided
        description: Specifies the stripe unit size of each disk
        in the architecture

    diskcount:
        required: true if disk_type is provided
        description: Specifies the number of data disks in the
        configuration.

author: Anusha Rao, Nandaja Varma
'''

EXAMPLES = '''
#Create Volume Groups on PVS /dev/sdb and /dev/sdc with
#physical extension size 128k
    - vg: action=create disks='["/dev/sdb", "/dev/sdc"]'
          options="--physicalextentsize 128k"
          vg_pattern="RHS_vg"
#Remove Volume Groups RHS_vg1, RHS_vg2 and RHS_vg3
    - pv: action=remove
          vg_name='["RHS_vg1", "RHS_vg2", "RHS_vg3"]'

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
        if not self.vgname:
            self.module.exit_json(msg="Nothing to be done")
        if self.action == 'create':
            self.disks = self.validated_params('disks')
            if not self.disks:
                self.module.exit_json(msg="Nothing to be done")
            self.options = self.module.params['options'] or ''
            self.vg_create()
        elif self.action == 'remove':
            self.vg_remove(self.vgname)
        elif self.action == 'extend':
            self.vg_extend()
        else:
            self.module.fail_json(msg="Unknown action")

    def validated_params(self, opt):
        value = self.module.params[opt]
        if value is None:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(msg=msg)
        return value

    def compute_size(self):
        self.stripe_unit_size = self.validated_params('stripesize')
        self.diskcount = self.validated_params('diskcount')
        pe_size = int(self.stripe_unit_size) * int(self.diskcount)
        return pe_size

    def vg_create(self):
        self.disktype = self.module.params['disktype']
        if self.disktype and self.disktype not in ['jbod']:
            self.options += ' -s %sK ' % self.compute_size()
        opts = " %s %s %s" % (self.vgname, self.options, self.disks)
        rc, out, err = self.run_command(self.op, opts)
        if rc != 0:
            self.vg_extend()
        self._get_output(rc, out, err)

    def vg_extend(self):
        self.op = 'vgextend'
        if not hasattr(self, 'disks'):
            self.disks = self.validated_params('disks')
        opts = " %s %s" % (self.vgname, self.disks)
        rc, out, err = self.run_command(self.op, opts)
        self._get_output(rc, out, err)

    def _get_output(self, rc, output, err):
        if not rc:
            self.module.exit_json(rc=rc, stdout=output, changed=1)
        else:
            self.module.fail_json(rc=rc, msg=err)

    def vg_remove(self, vgname):
        vg_absent = self.run_command('vgdisplay', ' ' + vgname)
        if not vg_absent[0]:
            opts = " -y -ff " + vgname
            rc, out, err = self.run_command(self.op, opts)
        else:
            rc, out, err =  vg_absent
        self._get_output(rc, out, err)

    def run_command(self, op, opts):
        cmd = self.module.get_bin_path(op, True) + opts
        if self.module.check_mode == True:
            try:
                from gdeploylib import Global
                Global.command = cmd
            except:
                pass
            self.module.exit_json(changed=False)
        return self.module.run_command(cmd)

if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(choices=["create", "remove", "extend"], required=True),
            vgname=dict(type='str'),
            disks=dict(),
            options=dict(type='str'),
            diskcount=dict(),
            disktype=dict(),
            stripesize=dict()
        ),
        supports_check_mode=True
    )

    vgops = VgOps(module)
