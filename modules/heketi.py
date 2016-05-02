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
from ast import literal_eval
import jwt
import datetime
import hashlib
import requests
import time
import json
import sys
from heketi import HeketiClient

class Heketi(HeketiClient):

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
        filename = self.module.params['filename']
        if filename:
            op = 'heketi-cli'
            cmd = ' load -json=%s' % filename
            rc, out, err = self.run_command(op, cmd)
            self.get_output(rc, out, err)
        else:
            self.init_heketi()
            cluster_id = self.module.params['cluster'] or  self.heketi_cluster_create()
            node_id = self.heketi_add_node(cluster_id)
            dev = self.heketi_add_device(node_id)
            result = {"cluster_id": cluster_id, "node_id": node_id,
                    "device_create": dev}
            self.module.exit_json(msg=result,rc=0, changed=1)

    def init_heketi(self):
        user = self._validated_params('sshuser')
        key = self._validated_params('userkey')
        server = self._validated_params('server')
        self.heketi = HeketiClient(server, user, key)

    def heketi_add_node(self, cluster_id):
        hostname = {}
        try:
            zone = self._validated_params('zone')
            hostname["manage"] = [self._validated_params('managehost')]
            hostname["storage"] = [self._validated_params('storagehost')]
        except:
            return
        node_dict = dict(zone=int(zone),hostnames=hostname,cluster=cluster_id)
        ret = self.heketi.node_add(node_dict)
        return ret['id']

    def heketi_add_device(self, node_id):
        try:
            devices = self._validated_params('devices')
        except:
            return False
        devices = literal_eval(devices)
        dev_dict = {}
        dev_dict["node"] = node_id
        for dev in devices:
            dev_dict["name"] = dev
            ret = self.heketi.device_add(dev_dict)
        return True

    def heketi_cluster_create(self):
        ret = self.heketi.cluster_create()
        return  ret['id']


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
            sshuser=dict(),
            userkey=dict(),
            managehost=dict(),
            storagehost=dict(),
            devices=dict(),
            cluster=dict(),
            zone=dict(),
        ),
    )

    hkt = Heketi(module)
    cmd = hkt.hkt_action()
