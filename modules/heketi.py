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

class HeketiClient(object):

    def __init__(self, host, user, key):
        self.host = host
        self.user = user
        self.key = key


    def _set_token_in_header(self, method, uri, headers = {}):
        claims = {}
        claims['iss'] = self.user

        # Issued at time
        claims['iat'] = datetime.datetime.utcnow()

        # Expiration time
        claims['exp'] = datetime.datetime.utcnow() \
                    + datetime.timedelta(seconds=1)

        # URI tampering protection
        claims['qsh'] = hashlib.sha256(method + '&' + uri).hexdigest()

        token = jwt.encode(claims, self.key, algorithm='HS256')
        headers['Authorization'] = 'bearer ' + token

        return headers


    def hello(self):
        method = 'GET'
        uri = '/hello'

        headers = self._set_token_in_header(method, uri)
        r = requests.get(self.host + uri, headers=headers)
        return r.status_code == requests.codes.ok


    def _make_request(self, method, uri, data={}, headers={}):
        headers = self._set_token_in_header(method, uri)

        ''' Ref: http://docs.python-requests.org/en/master/_modules/requests/api/#request '''
        r = requests.request(method,
                             self.host + uri,
                             headers=headers,
                             data=json.dumps(data))

        r.raise_for_status()

        if r.status_code == requests.codes.accepted:
            return self._get_queued_response(r.headers['location'])
        else:
            return r


    def _get_queued_response(self, queue_uri):
        queue_uri = queue_uri
        headers = self._set_token_in_header('GET', queue_uri)
        response_ready = False

        while response_ready is False:
            q = requests.get(self.host + queue_uri,
                             headers=headers,
                             allow_redirects=True)

            # Raise an exception when the request fails
            q.raise_for_status()

            if 'X-Pending' in q.headers:
                time.sleep(2)
            else:
                return q


    def cluster_create(self):
        req = self._make_request('POST', '/clusters')
        if req.status_code == requests.codes.created:
            return req.json()


    def cluster_info(self, cluster_id):
        uri = "/clusters/" + cluster_id
        req = self._make_request('GET', uri)
        if req.status_code == requests.codes.ok:
            return req.json()


    def cluster_list(self):
        uri = "/clusters"
        req = self._make_request('GET', uri)
        if req.status_code == requests.codes.ok:
            return req.json()


    def cluster_delete(self, cluster_id):
        uri = "/clusters/" + cluster_id
        req = self._make_request('DELETE', uri)
        return req.status_code == requests.codes.NO_CONTENT


    def node_add(self, node_options = {}):
        ''' node_options is a dict consisting of paramters for \
            adding a node: https://github.com/heketi/heketi/wiki/API#add-node '''
        uri = "/nodes"
        req = self._make_request('POST', uri, node_options)
        if req.status_code == requests.codes.ok:
            return req.json()


    def node_info(self, node_id):
        uri = '/nodes/' + node_id
        req = self._make_request('GET', uri)
        if req.status_code == requests.codes.ok:
            return req.json()

    def node_delete(self, node_id):
        uri = '/nodes/'+ node_id
        req = self._make_request('DELETE', uri)
        return req.status_code == requests.codes.NO_CONTENT


    def device_add(self, device_options = {}):
        ''' device_options is a dict with parameters to be passed \
            in the json request: \
            https://github.com/heketi/heketi/wiki/API#add-device
        '''
        uri = '/devices'
        req = self._make_request('POST', uri, device_options)
        if req.status_code == requests.codes.accepted:
            return req.json()


    def device_info(self, device_id):
        uri = '/devices/' + device_id
        req = self._make_request('GET', uri)
        if req.status_code == requests.codes.ok:
            return req.json()


    def device_delete(self, device_id):
        uri = '/devices/' + device_id
        req = self._make_request('DELETE', uri)
        return req.status_code == requests.codes.NO_CONTENT


    def volume_create(self, volume_options = {}):
        ''' volume_options is a dict with volume creation options:
            https://github.com/heketi/heketi/wiki/API#create-a-volume
        '''
        uri = '/volumes'
        req = self._make_request('POST', uri, volume_options)
        if req.status_code == requests.codes.ok:
            return req.json()


    def volume_list(self):
        uri = '/volumes'
        req = self._make_request('GET', uri)
        if req.status_code == requests.codes.ok:
            return req.json()


    def volume_info(self, volume_id):
        uri = '/volumes/' + volume_id
        req = self._make_request('GET', uri)
        if req.status_code == requests.codes.ok:
            return req.json()

    def volume_expand(self, volume_id, expand_size = {}):
        uri = '/volumes/' + volume_id + '/expand'
        req = self._make_request('POST', uri, expand_size )
        if req.status_code == requests.codes.ok:
            return req.json()


    def volume_delete(self, volume_id):
        uri = '/volumes/' + volume_id
        req = self._make_request('DELETE', uri)
        return req.status_code == requests.codes.NO_CONTENT

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
            print "yes"
            self.init_heketi()
            cluster_id = self.module.params['cluster'] or  self.heketi_cluster_create()
            node_id = self.heketi_add_node(cluster_id)
            dev_id = self.heketi_add_device(node_id)

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
        node_dict = str(dict(zone=zone,cluster=cluster_id,hostnames=hostname))
        ret = self.heketi.node_add(literal_eval(node_dict))
        return ret['id']


    def heketi_add_device(self, node_id):
        try:
            devices = literal_eval(self._validated_params('devices'))
        except:
            return
        dev_dict = {}
        dev_dict["node"] = node_id
        for dev in devices:
            dev_dict["name"] = dev
            ret = self.heketi.device_add(dev_dict)
        return ret['id']

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
