#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Ansible module to create or remove a Physical Volume.
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
ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'supported_by': 'community',
    'status': ['preview']
}
DOCUMENTATION = '''
---
authors: Nandaja Varma, Ashmitha Ambastha
module: pv
short_description: Create, remove, resize, and change a Physical Volume.
description:
    - Creates, removes, resizes, and changes a Physical Volume.

options:
    action:
        required: true
        choices: [create, remove, resize, change]
        description: Specifies the pv operation that is to be executed,
                     either a physical volume creation or deletion.
    disks:
        required: true
        description: Disks from which the Physical Volumes are to be created,
                     removed, resized and changed needs to be
                     specified here.
    size:
        required: true
        description: Specifies to what size the physical volume is to be
                     shrunken
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
#Create Physical Volumes /dev/vdb with dataalignment 1280k
    - pv: action=create disk=<disk name> for eg, /dev/vdb
          force='y'
          uuid=<uuid>
          zero='y'
      with_items:
         - disk1

#Remove Physical Volumes /dev/vdb
    - pv: action=remove disk=<disk name>
          force='y'
      with_items:
         - disk1

'''

from ansible.module_utils.basic import AnsibleModule


class PvOps(object):

    def __init__(self, module):
        self.module = module
        self.action = self.validated_params('action')

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
            self.module.exit_json(rc=0, changed=0, msg="%s Physical Volume"
                                  " Exists!" % disk)
        elif self.action == 'remove' and rc:
            self.module.exit_json(rc=0, changed=0, msg="%s Physical Volume"
                                  "Doesn't Exists!" % disk)
        else:
            ret = 1
        return ret

    def pv_action(self):
        self.disk = self.module.params['disk']
        if not self.disk:
            self.disk = self.module.params['disks']
            print('disks paramater is deprecated, please use disk')
        return self.get_volume_command(self.disk)

    def get_volume_command(self, disk):
        args = ' ' + str(disk)

        if self.action == 'create':
            force = self.module.params['force']
            if force == 'y':
                args += " -f"
            uuid = self.module.params['uuid']
            if uuid:
                args += " -u " + uuid
                args += " --norestorefile"
            zero = self.module.params['zero']
            if zero:
                args += " -Z y "
            metadatasize = self.module.params['metadatasize']
            if metadatasize:
                args += " --metadatasize " + metadatasize
            dataalignment = self.module.params['dataalignment']
            if dataalignment:
                args += " --dataalignment " + dataalignment
        elif self.action == 'remove':
            force = self.module.params['force']
            if force == 'y':
                args += " -f"
        elif self.action == 'change':
            uuid = self.module.params['uuid']
            if uuid:
                args += " -u " + uuid
                # args += " --norestorefile"
            metadataignore = self.module.params['metadataignore']
            if metadataignore == 'y':
                args += " --metadataignore " + metadataignore
            allocatable = self.module.params['allocatable']
            if allocatable == 'n':
                args += " -x " + allocatable
        elif self.action == 'resize':
            setphysicalvolumesize = self.module.params['setphysicalvolumesize']
            if setphysicalvolumesize:
                args += " --setphysicalvolumesize " + setphysicalvolumesize
        return args


if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(choices=["create", "remove", "resize", "change"], required=True),
            disks=dict(),
            disk=dict(),
            force=dict(type='str'),
            uuid=dict(type='str'),
            zero=dict(type='str'),
            metadatasize=dict(type='str'),
            metadataignore=dict(type='str'),
            setphysicalvolumesize=dict(type='str'),
            allocatable=dict(type='str'),
            dataalignment=dict(type='str'),
            size=dict(),
        ),
    )

    pvops = PvOps(module)
    cmd = pvops.pv_action()
    pvops.pv_presence_check(pvops.disk)
    rc, out, err = pvops.run_command('pv' + pvops.action, cmd)
    pvops.get_output(rc, out, err)
