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
ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'supported_by': 'redhat',
    'status': ['preview']
}
DOCUMENTATION = '''
---
authors: Nandaja Varma, Ashmitha Ambastha
module: pv
short_description: Create, remove, resize and change a Physical Volume.
description:
    - Creates, removes,resizes and changes a Physical Volume.

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
    size:
        required: true
        description: Specifies to what size the physical volume is to be
                     shrunken
    force:
        required: true
        description: Force  the  creation  without  any confirmation.
    uuid:
        required: true
        description: Specify the uuid for the device.  Without this option,
                     pvcreate generates a random uuid.
    zero:
        required: true
        description: Whether or not the first 4 sectors of the device should
                     be wiped.
    metadatasize:
        required: true
        description: The approximate amount of space to be set aside for
                     each metadata area.
    dataalignment:
        required: true
        description: Align the start of the data to a multiple of this number.

'''

EXAMPLES = '''
#Create Physical Volumes /dev/sdb and /dev/sdc with
#dataalignment 1280k
    - pv: action=create disks='["/dev/sdb", "/dev/sdc"]'
          options="--dataalignment 1280k"
          force=['y']
          uuid=[88x2Wj-ki7V-aSF6-79jh-ORum-lEd8-w66h5d]
          zero=['y']

#Remove Physical Volumes /dev/sdb and /dev/sdc
    - pv: action=remove disks='["/dev/sdb", "/dev/sdc"]'
          force=['y']

'''
from ansible.module_utils.basic import *
import json
from ast import literal_eval


class PvOps(object):

    def __init__(self, module):
        self.module = module
        self.action = self.validated_params('action')
        # self.options = self.module.params['options'] or ''

    def validated_params(self, opt):
        value = self.module.params[opt]
        if value is None:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(rc=1, msg=msg)
        return value

    def run_command(self, op, options):
        cmd = self.module.get_bin_path(op, True)  + options
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
            self.module.exit_json(rc=0, changed= 0, msg="%s Physical Volume"
                                   " Exists!" % disk)
        elif self.action == 'remove' and rc:
            self.module.exit_json(rc=0, changed=0,msg="%s Physical Volume"
                                   "Doesn't Exists!" % disk)
        else:
            ret=1
        return ret

    def pv_action(self):
        self.disks = self.validated_params('disks')
        if not self.disks:
            self.module.exit_json(msg="Nothing to do")
        return self.get_volume_command(self.disks)


    def get_volume_command(self, disk):
        self.module.exit_json("Warning! Disks is deprecated. Use disk")
        op = 'pv' + self.action
        args = " %s %s" % (self.options, disk)
        force = self.module.params('force')
        if force == 'y' and self.action in ['create', 'remove']:
            args += "-f"
        uuid = self.module.params('uuid')
        if uuid and self.action in ['create','pvchange']:
            args += "-u " + uuid
        zero = self.module.params('zero')
        if zero and self.action == 'create':
            args += "-z"
        metadatasize = self.module.params('metadatasize')
        if metadatasize and self.action == 'create':
            args += "--metadatasize " + metadatasize
        metadataignore = self.module.params('metadataignore')
        if metadataignore == 'y' and self.action in ['change']:
            args += "--metadataignore"
        allocatable = self.module.params('allocatable')
        if allocatable and self.action == 'change':
            args += "--allocatable" + allocatable
        setphysicalvolumesize = self.module.params('setphysicalvolumesize')
        if setphysicalvolumesize and self.action == 'resize':
            args += "--setphysicalvolumesize" + setphysicalvolumesize
        return args


if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(choices=["create", "remove", "resize", "change"], required=True),
            disk=dict(),
            # options=dict(type='str'),
            force=dict(type='str'),
            uuid=dict(typ='str'),
            zero=dict(typ='str'),
            metadatasize=dict(type='str'),
            metadataignore=dict(typ='str'),
            setphysicalvolumesize=dict(typ='str'),
            size=dict(),
        ),
    )

    pvops = PvOps(module)
    cmd = pvops.pv_action()
    pvops.pv_presence_check(pvops.disks)
    rc, out, err = pvops.run_command('pv' + pvops.action, cmd)
    pvops.get_output(rc, out, err)
