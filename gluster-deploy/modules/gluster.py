#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2015 Nandaja Varma <nvarma@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import sys
import json
from ansible.module_utils.basic import *
from ast import literal_eval

class Gluster(object):
    def __init__(self, module):
        self.module = module
        self.command = self._validated_params('command')
        self.action = self._validated_params('action')
        '''current_host(the one in which operation is running right now) and
           hosts can be defined in the yml like this
           current_host={{inventory_hostname}}
           hosts="{% for host in groups[<group name>] %}
           {{ hostvars[host]['private_ip'] }},{% endfor %}"

        '''
        self.current_host = self._validated_params('current_host')
        self.hosts = literal_eval(self._validated_params('hosts'))
        {
            'peer': self.gluster_peer_ops,
            'volume': self.gluster_volume_ops
        }[self.command]()

    def _validated_params(self, opt):
        value = self.module.params[opt]
        if value is None:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(msg=msg)
        return value

    def gluster_peer_ops(self):
        if self.action in ['probe', 'detach']:
            force = 'force' if self.module.params['force'] == 'yes' else ''
            peers = [peer for peer in self.hosts
                    if peer not in self.current_host]
            for hostname in peers:
                rc, output, err = self.call_gluster_cmd('peer',
                        self.action, force, hostname)
        else:
            rc, output, err = self.call_gluster_cmd('peer', self.action)
            #This still doesn't print output to stdout sadly.
        self._get_output(rc, output, err)

    def gluster_volume_ops(self):
        #ops = ['create', 'delete', 'set', 'add-brick', 'remove-brick']
        if self.action == 'create':
            force = 'force' if self.module.params['force'] == 'yes' else ''
            self.bricks = [brick.strip('[]\n\t\r') for brick in
                    self._validated_params('bricks').split(' ') if brick]
            brick_list = ' '.join(brick_path for brick_path in
                    self.append_host_name())
            volume = self._validated_params('volume')
            rc, out, err = self.call_gluster_cmd('volume',
                    self.action, volume, brick_list, force)
        else:
            rc = 1
            out = ''
            err = 'Not yet'
        self._get_output(rc, out, err)



    def append_host_name(self):
        brick_list = []
        for host, brick in zip(self.hosts, self.bricks):
            brick_list.append(host + ':' + brick)
        return brick_list

    def call_gluster_cmd(self, *args):
        params = ' '.join(opt for opt in args)
        return self._run_command('gluster', ' ' + params)

    def _get_output(self, rc, output, err):
        if not rc:
            self.module.exit_json(stdout=output)
        else:
            self.module.fail_json(msg=err)

    def _run_command(self, op, opts):
        cmd = self.module.get_bin_path(op, True) + opts
        return self.module.run_command(cmd)

if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            command=dict(required=True),
            action=dict(required=True),
            current_host=dict(required=True),
            hosts=dict(required=True),
            volume=dict(),
            bricks=dict(),
            force=dict()
        ),
    )

    Gluster(module)
