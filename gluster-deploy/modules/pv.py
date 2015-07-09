#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Ansible module to create or remove a Physical Volume.
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
module: pv
short_description: Create or remove a Physical Volume.
description:
    - Creates or removes n-number of Physical Volumes on n-number
      of remote hosts

options:
    action:
        required: true
        choices: [create, remove, resize, change]
        description: Specifies the pv operation that is to be executed,
                     either a physical volume creation or deletion.
    disks:
        required: true
        description: Disks from which the Physical Volumes are to be created,
                     or Physical Volumes that are to be removed needs to be
                     specified here.
    options:
        required: false
        description: Extra options that needs to be passed while creating the
                     Physical Volumes can be given here. Check the man page of
                     pvcreate for more info.
    operation:
        required: true if action is resize
        choices: [expand, shrink]
        description: Specifies how the physical volume should be resized.
                     Either to expand or shrink
    size:
        required: true if action is resize and opertion is shrink
        description: Specifies to what size the physical volume is to be
                     shrunken

authors: Anusha Rao, Nandaja Varma
'''

EXAMPLES = '''
#Create Physical Volumes /dev/sdb and /dev/sdc with
#dataalignment 1280k
    - pv: action=create disks='["/dev/sdb", "/dev/sdc"]'
          options="--dataalignment 1280k"
#Remove Physical Volumes /dev/sdb and /dev/sdc
    - pv: action=remove disks='["/dev/sdb", "/dev/sdc"]'
'''
from ansible.module_utils.basic import *
import json
from ast import literal_eval


class PvOps(object):

    def __init__(self, module):
        self.result = {'clears': [], 'errors': []}
        self.module = module
        self.action = self.validated_params('action')
        self.options = self.module.params['options'] or ''
        self.pv_action()
        self.get_output()

    def get_output(self):
        if not self.result['errors']:
            self.module.exit_json(msg=self.result['clears'], changed=1)
        else:
            self.module.fail_json(msg=self.result['errors'])

    def validated_params(self, opt):
        value = self.module.params[opt]
        if value is None:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(msg=msg)
        return value

    def run_command(self, op, options):
        cmd = self.module.get_bin_path(op, True)  + options
        rc, output, err = self.module.run_command(cmd)
        if op == 'pvdisplay':
            return rc
        elif rc:
            self.result['errors'].append(err)
        else:
            self.result['clears'].append(output)


    def pv_presence_check(self, disk):
        rc = self.run_command('pvdisplay', ' ' + disk)
        ret = 0
        if self.action == 'create' and not rc:
            self.result['errors'].append(
                "%s Physical Volume Exists!" %
                disk)
        elif self.action == 'remove' and rc:
            self.result['errors'].append(
                "%s Physical Volume Does Not Exist!" % disk)
        else:
            ret = 1
        return ret

    def iterate_disk_names(self):
        self.disks = literal_eval(self.validated_params('disks'))
        map(self.call_ansible_run_command, self.disks)

    def get_resize_params(self, disk):
        size = self.validated_params('size')
        params = " %s --setphysicalvolumesize %s %s " % (self.options, size, disk)
        if self.pv_presence_check(disk):
            self.run_command('pvresize', params)

    def resize(self):
        self.operation = self.validated_params('operation')
        if self.operation == 'expand':
            self.iterate_disk_names()
        else:
            disks = self.validated_params('disks'),
            map(self.get_resize_params, disks)

    def call_ansible_run_command(self, disk):
        if self.pv_presence_check(disk):
            op = 'pv' + self.action
            args = " %s %s" % (self.options, disk)
            self.run_command(op, args)

    def pv_action(self):
        if self.action == 'resize':
            self.resize()
        else:
            self.iterate_disk_names()

if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(choices=["create", "remove", "resize", "change"], required=True),
            disks=dict(),
            options=dict(type='str'),
            size=dict(),
            operation=dict(choices=["expand", "shrink"]),
        ),
    )

    pvops = PvOps(module)
