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
        self.init_values()

    def init_values(self):
        if self.action == 'create':
            self.disks = self.validated_params('disks')
            self.vgname = self.validated_params('vgname')
            self.options = self.module.params['options'] or ''
            if self.disks == "['setup']" or self.disks == 'setup':
                self.find_disks()
            else:
                output = self.vg_create()
                if output[0]:
                    self.module.fail_json(msg=output[2])
                else:
                    self.module.exit_json(msg=output[1], changed=1)
        else:
            self.vgname = literal_eval(self.validated_params('vgname'))
            output = map(self.vg_remove, self.vgname)
            self.get_output(output)

    def find_disks(self):
        rc, output, err = self.module.run_command(
                "lsblk -o name,mountpoint")
        disks = [line.strip().split(' ') for
            line in output.split('\n') if len(line.strip().split(' ')) == 1]
        disks = [s[0].decode('unicode_escape').encode(
            'ascii','ignore') for s in filter(None, disks)]
        for disk in disks:
            dgroup = re.match('([v,s]d.)[0-9]*.*', disk)
            if dgroup:
                root_partition = dgroup.group(1)
                break
        all_disks = filter(lambda x: not re.match(
            root_partition + '.*', x), filter(None, disks))
        disks = map(lambda x: '/dev/' + x, all_disks)
        options = []
        for i in range(1, len(self.disks) + 1):
            options.append(self.vgname + str(i))
        vgname = options
        error, success = [], []
        for disk, vg in zip(disks, vgname):
            self.vgname  = vg
            self.disks = disk
            output = self.vg_create()
            if output[0] != 0:
                error.append(output[2])
            else:
                success.append(output[1])
        if error:
            self.module.fail_json(msg=error)
        else:
            self.module.exit_json(msg=success, changed=1)

    def get_output(self, output):
        for each in output:
            if each[0]:
                self.module.fail_json(msg=each[2])
            else:
                self.module.exit_json(msg=each[1], changed=1)

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
        return self.run_command(self.op, opts)

    def vg_remove(self, vgname):
        vg_absent = self.run_command('vgdisplay', ' ' + vgname)
        if not vg_absent[0]:
            opts = " -y -ff " + vgname
            return self.run_command(self.op, opts)
        else:
            return vg_absent

    def run_command(self, op, opts):
        cmd = self.module.get_bin_path(op, True) + opts
        return self.module.run_command(cmd)

if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(choices=["create", "remove"], required=True),
            vgname=dict(type='str'),
            disks=dict(),
            options=dict(type='str'),
            diskcount=dict(),
            disktype=dict(),
            stripesize=dict()
        ),
    )

    vgops = VgOps(module)
