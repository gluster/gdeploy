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
        self.action = self._get_params('action')
        self.init_heketi()

    def hkt_action(self):
        msg = {
                 'load': self.load_topology,
                 'addnode': self.heketi_add_node,
                 'adddevice': self.heketi_add_device,
                 'createvolume': self.heketi_create_volume
              }[self.action]()
        return msg


    def _get_params(self, opt, reqd=True):
        value = self.module.params[opt]
        if (value is None or not value.strip(" ")) and reqd:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(rc=1, msg=msg)
        value = value.strip() if value else value
        return value

    def load_topology(self):
        filename = self._get_params('filename', False)
        if filename:
            op = 'heketi-cli'
            cmd = ' load -json=%s' % filename
            rc, out, err = self.run_command(op, cmd)
            self.get_output(rc, out, err)
        else:
            cluster_id = self.heketi_cluster_create()
            node_id = self.heketi_add_node(cluster_id)
            dev = self.heketi_add_device(node_id)
            result = {"cluster_id": cluster_id, "node_id": node_id,
                    "device_create": dev}
            return result

    def init_heketi(self, server=None):
        user = self._get_params('sshuser')
        key = self._get_params('userkey')
        server = self._get_params('server', False)
        if not server:
            hostnames = self._get_params('hostnames')
            hostnames = literal_eval(hostnames)
            for host in hostnames:
                self.heketi = HeketiClient(host, user, key)
                try:
                    self.heketi.hello()
                    server = host
                except:
                    pass
        if not server:
            self.module.fail_json(msg="Could not find the heketi service")
        self.heketi = HeketiClient(server, user, key)

    def heketi_add_node(self, cluster_id=None):
        if not cluster_id:
            cluster_id = self._get_params('cluster')
        hostname = {}
        zone = self._get_params('zone', False)
        hostname["manage"] = [self._get_params('managehost', False)]
        hostname["storage"] = [self._get_params('storagehost', False)]
        if not (zone and hostname["manage"] and hostname["storage"]):
            return False
        node_dict = dict(zone=int(zone),hostnames=hostname,cluster=cluster_id)
        ret = self.heketi.node_add(node_dict)
        return ret['id']

    def heketi_add_device(self, node_id=None):
        if not node_id:
            node_id = self._get_params('node', False)
        if not node_id:
            return ''
        try:
            devices = self._get_params('devices')
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
        cid = self._get_params('cluster', False)
        if cid:
            return cid
        ret = self.heketi.cluster_create()
        return  ret['id']

    def heketi_create_volume(self):
        vol = {}
        vol["size"] = int(self._get_params('size'))

        vname = self._get_params('name', False)
        if vname:
            vol['name'] = vname

        snapshot = self._get_params('snapshot', False)
        if snapshot and snapshot == 'true':
            vol['snapshot'], h = {}, {}
            h['enable'] = "true"
            f = self._get_params('snapshot_factor', False)
            if f:
                h['factor'] = int(f)
            vol['snapshot'] = h

        durability = self._get_params('durability', False)
        if durability and durability.lower() != 'none':
            vol['durability'], h = {}, {}
            if durability.lower() == 'replicate':
                h['type'] = 'replicate'
                c = self._get_params('replica_count', False)
                if c:
                    h['replicate'] = {'replica': int(c)}
            if durability.lower() == 'disperse':
                h['type'] = 'disperse'
                d = self._get_params('disperse_data', False)
                r = self._get_params('redundancy', False)
                h['disperse'] = {'data': int(d), 'redundancy': int(r)}
                h = dict((k, v) for k, v in h.iteritems() if v)
            vol['durability'] = h

        clusters = self._get_params('clusters', False)
        if clusters:
            vol['clusters'] = clusters
        ret = self.heketi.volume_create(vol)
        return ret


    def run_command(self, op, options):
        cmd = self.module.get_bin_path(op, True)  + options
        return self.module.run_command(cmd)

    def get_output(self, output):
        self.module.exit_json(msg=output, changed=1)

if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(choices=["load", "addnode", "adddevice",
            "createvolume"], required=True),
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
            node=dict(),
            size=dict(),
            snapshot=dict(),
            snapshot_factor=dict(),
            durability=dict(),
            replica_count=dict(),
            disperse_data=dict(),
            redundancy=dict(),
            clusters=dict(),
            name=dict(),
            hostnames=dict()
        ),
    )

    hkt = Heketi(module)
    out = hkt.hkt_action()
    hkt.get_output(out)
