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

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = '''
---
module: pv
short_description: Create, remove, resize or change a Physical Volume.
description:
    - Creates or removes n-number of Physical Volumes on n-number
      of remote hosts

options:
    action:
        required:    true
        choices:     [create, remove, resize, change]
        description: * Specifies the pv operation that is to be executed,
                       either a physical volume creation or deletion.

                     * PV Resize to a manually specified size is done via options:
                        --setphysicalvolumesize <Size[m|UNIT]>
                        --yes / -y is required for shrinking (potentially dangerous)

                     * PV change requires additional options, check 'pvchange' man page

    disks:
        required:    true
        description: Disks from which the Physical Volumes are to be created,
                     or Physical Volumes that are to be removed needs to be
                     specified here.
    options:
        required:    false
        description: Extra options that needs to be passed while creating the
                     Physical Volumes can be given here. Check the man page of
                     pvcreate for more info.

authors: Anusha Rao, Nandaja Varma
'''

EXAMPLES = '''
#Create Physical Volumes /dev/sdb and /dev/sdc with
#dataalignment 1280k
    - pv: action=create disks="{{ item }}"
          options="--dataalignment 1280k"
      with_items:
         - disk1
         - disk2

#Remove Physical Volumes /dev/sdb and /dev/sdc
    - pv: action=remove disks="{{ item }}"
      with_items:
         - disk1
         - disk2

#Resize/Shrink Physical Volume /dev/sdb
    - pv:
        action: resize
        disks: "/dev/sdb"
        options: "--setphysicalvolumesize 1000G --yes"
'''


class PvOps(object):

    def __init__(self, module):
        self.module = module
        self.action = self.validated_params('action')
        self.options = self.module.params['options'] or ''

    def validated_params(self, opt):
        value = self.module.params[opt]
        if value is None:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(rc=1, msg=msg)
        return value

    def run_command(self, op, options):
        cmd = self.module.get_bin_path(op, True) + options
        return self.module.run_command(cmd)

    def get_output(self, rc, output, err):
        if not rc:
            self.module.exit_json(rc=rc, stdout=output, changed=1)
        else:
            self.module.fail_json(rc=rc, msg=err)

    def pv_presence_check(self, disk):
        rc, out, err = self.run_command('pvdisplay', ' ' + disk)
        ret = 0
        if self.action == 'create' and not rc:
            self.module.exit_json(
                rc=0, changed=0, msg="%s Physical Volume Exists!" % disk)
        elif self.action == 'remove' and rc:
            self.module.exit_json(
                rc=0, changed=0, msg="%s Physical Volume Doesn't Exists!" % disk)
        else:
            ret = 1
        return ret

    def pv_action(self):
        self.disks = self.validated_params('disks')
        if not self.disks:
            self.module.exit_json(msg="Nothing to do")
        return self.get_volume_command(self.disks)

    def get_volume_command(self, disk):
        args = " %s %s" % (self.options, disk)
        return args


if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(choices=["create", "remove",
                                 "resize", "change"], required=True),
            disks=dict(),
            options=dict(type='str'),
        ),
    )

    pvops = PvOps(module)
    cmd = pvops.pv_action()
    pvops.pv_presence_check(pvops.disks)
    rc, out, err = pvops.run_command('pv' + pvops.action, cmd)
    pvops.get_output(rc, out, err)
