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
import pdb

class BackendReset(object):

    def __init__(self, module):
        self.output = []
        self.module = module
        self.pvs = self.validated_params('pvs')
        self.vgs = self.validated_params('vgs')
        self.lvs = self.validated_params('lvs')
        self.unmount = self.validated_params('unmount')
        self.mountpoints = self.validated_params('mountpoints')
        self.remove_lvs()
        self.remove_vgs()
        self.remove_pvs()
        errors = [output[2] for output in self.output if output[0] != 0]
        messages = [output[1] for output in self.output if output[0] == 0]
        if not errors:
            self.module.exit_json(changed=1)
        else:
            out = '\n'.join(errors)
            if messages:
                out += 'Succeeded operations are:\n' + '\n'.join(messages)
            self.module.fail_json(msg=out,rc=1)

    def validated_params(self, opt):
        value = self.module.params[opt]
        if value is None:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(rc=1, msg=msg)
        return value

    def run_command(self, op, options):
        cmd = self.module.get_bin_path(op, True)  +  ' ' + options
        return self.module.run_command(cmd)

    def remove_pvs(self):
        if not self.pvs:
            return
        if not type(self.pvs) is list:
            self.pvs = literal_eval(self.pvs)
        options = ' -y -ff ' + ' '.join(self.pvs)
        rc, out, err = self.run_command('pvremove', options)
        self.output.append([rc, out, err])

    def remove_vgs(self):
        self.get_vgs()
        if not self.vgs:
            return

        if not type(self.vgs) is list:
            self.vgs = literal_eval(self.vgs)
        options = ' -y -ff ' + ' '.join(self.vgs)
        rc, out, err = self.run_command('vgremove', options)
        self.output.append([rc, out, err])

    def remove_lvs(self):
        self.get_lvs()
        if not self.lvs:
            return
        if not type(self.vgs) is list:
            self.vgs = literal_eval(self.vgs)
        if not self.mountpoints:
            self.mountpoints = self.lvs
        self.umount_bricks()
        options = ' -y ' + ' '.join(self.lvs)
        rc, out, err = self.run_command('lvremove', options)
        self.output.append([rc, out, err])

    def umount_bricks(self):
        if literal_eval(self.unmount)[0].lower() != 'yes':
            return
        if not self.mountpoints:
            return
        if not type(self.mountpoints) is list:
            self.mountpoints = literal_eval(self.mountpoints)
        rc, out, err = self.run_command('umount', ' '.join(
            self.mountpoints))

    def get_vgs(self):
        if self.vgs:
            return
        if self.pvs:
            option = " --noheading -o vg_name %s" % self.pvs
            rc, vgs, err = self.run_command('pvs', option)
            self.vgs = filter(None, [vg.strip() for
                vg in vgs.split(' ')])


    def get_lvs(self):
        if self.lvs:
            self.format_lvnames()
            return
        if not self.vgs:
            self.get_vgs()
        if not type(self.vgs) is list:
            self.vgs = literal_eval(self.vgs)
        self.lvs = []
        if self.vgs:
            for vg in self.vgs:
                option = " --noheading -o lv_name %s" % vg
                rc, out, err = self.run_command('vgs', option)
                lvs = [x.strip() for x in out.split(' ')]
                self.lvs.extend(['/dev/' + vg.strip() + '/' + lv for lv in filter(
                    None, lvs)])

    def format_lvnames(self):
        if not type(self.lvs) is list:
            self.lvs = literal_eval(self.lvs)
        formatted_lvname = [True for lv in self.lvs if lv.startswith(
            '/dev/')]
        if True not in formatted_lvname:
            option = " --noheading -o vg_name"
            rc, vgs, err = self.run_command('vgs', option)
            vg_list = filter(None, [x.strip() for x in vgs.split(' ')])
            lv_list = []
            for vg in vg_list:
                option = " --noheading -o lv_name %s" % vg
                rc, out, err = self.run_command('vgs', option)
                lvs = [x.strip() for x in out.split()]
                for lv in lvs:
                    if lv in self.lvs:
                        lv_list.append('/dev/' + vg + '/' + lv)

            self.lvs = lv_list


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
