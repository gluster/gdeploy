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
from ansible.module_utils.basic import *
import json
from ast import literal_eval


class Heketi(object):

    def __init__(self, module):
        self.module = module
        self.action = self._validated_params('action')

    def hkt_action(self):
        if self.action == 'load':
            return self.load_topology()

    def _validated_params(self, opt):
        value = self.module.params[opt]
        if value is None:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(rc=1, msg=msg)
        return value

    def load_topology(self):
        filename = self._validated_params('filename')
        op = 'heketi-cli'
        cmd = ' load -json=%s' % filename
        rc, out, err = self.run_command(op, cmd)
        self.get_output(rc, out, err)

    def run_command(self, op, options):
        cmd = self.module.get_bin_path(op, True)  + options
        return self.module.run_command(cmd)

    def get_output(self, rc, output, err):
        if not rc:
            self.module.exit_json(rc=rc, stdout=output, changed=1)
        else:
            self.module.fail_json(rc=rc, msg=err)

if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(choices=["load"], required=True),
            filename=dict(),
            server=dict(),
            port=dict(),
        ),
    )

    hkt = Heketi(module)
    cmd = hkt.hkt_action()
