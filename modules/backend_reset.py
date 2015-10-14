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
'''

EXAMPLES = '''
'''
from ansible.module_utils.basic import *
import json
from ast import literal_eval

class BackendReset(object):

    def __init__(self, module):
        self.output = []
        self.module = module
        self.pvs = self.validated_params('pvs')
        self.vgs = self.validated_params('vgs')
        self.lvs = self.validated_params('lvs')
        self.unmount = self.validated_params('unmount')
        self.mountpoints = self.validated_params('mountpoints')
        self.umount()
        self.remove_lvs()
        self.remove_vgs()
        self.remove_pvs()
        if not self.output:
            self.module.exit_json()
        errors = [output[2] for output in self.output if output[0] != 0]
        self.module.fail_json(rc=1, msg=errors)

    def validated_params(self, opt):
        value = self.module.params[opt]
        if value is None:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(rc=1, msg=msg)
        return value

    def run_command(self, op, options):
        cmd = self.module.get_bin_path(op, True)  +  ' ' + options
        return self.module.run_command(cmd)

    def _get_output(self, rc, output, err):
        if not rc:
            self.module.exit_json(rc=rc, stdout=output, changed=1)
        else:
            self.module.fail_json(rc=rc, msg=err)

    def remove_pvs(self):
        if not self.pvs:
            return
        rc, out, err = self.run_command('pvremove', self.pvs)
        self.output.append([rc, out, err])

    def remove_vgs(self):
        self.get_vgs()
        if not self.vgs:
            return

        options = ' -y ff ' + self.vgs
        rc, out, err = self.run_command('vgremove', options)
        self.output.append([rc, out, err])

    def remove_lvs(self):
        self.get_lvs()
        if not self.lvs:
            return
        options = ' -y ' + ' '.join(self.lvs)
        rc, out, err = self.run_command('lvremove', options)
        self.output.append([rc, out, err])

    def umount(self):
        if self.unmount.lower() != 'yes':
            return
        self.get_mountpoints()
        if not self.mountpoints:
            return
        rc, out, err = self.run_command('umount', ' '.join(
            self.mountpoints))
        self.output.append([rc, out, err])

    def get_vgs(self):
        if self.vgs:
            return
        if self.pvs:
            option = " --noheading -o vg_name %s" % self.pvs
            rc, self.vgs, err = self.run_command('pvs', option)
        else:
            option = " --noheading -o vg_name"
            rc, vgs, err = self.run_command('vgs', option)
            vg_list = filter(None, [x.strip() for x in vgs.split(' ')])
            for vg in vg_list:
                lvs = []
                option = " --noheading -o lv_name %s" % vg
                rc, out, err = self.run_command('vgs', option)
                lvs = [x.strip() for x in out.split()]

            if not set(lvs).intersection(set(self.lvs)):
                vg_list.remove(vg)
            return vg_list


    def get_lvs(self):
        self.module.fail_json(msg=self.lvs)
        if self.lvs and self.lvs.startswith('/dev'):
            return
        if self.lvs:
            self.lvs = literal_eval(self.lvs)
            vgs = self.get_vgs()
            self.lvs = ['/dev/' + vg + '/' + lv for vg, lv in zip(
                vgs, self.lvs)]
            return
        if not self.vgs:
            self.get_vgs()
        if self.vgs:
            option = " --noheading -o lv_name %s" % self.vgs
            rc, self.lvs, err = self.run_command('vgs', option)
            lvs = [x.strip() for x in self.lvs.split(' ')]
            self.lvs = ['/dev/' + self.vgs.strip() + '/' + lv for lv in filter(
                None, lvs)]
        else:
            self.lvs = ''

    def get_mountpoints(self):
        if self.mountpoints:
            return
        if not self.lvs:
            self.get_lvs()
        self.mountpoints = self.lvs



if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            pvs=dict(),
            vgs=dict(),
            lvs=dict(type='str'),
            unmount=dict(),
            mountpoints=dict(),
        ),
    )

    BackendReset(module)
