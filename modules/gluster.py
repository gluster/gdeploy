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
        self.force = 'force' if self.module.params['force'] == 'yes' else ''
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

    def get_host_names(self):
        '''current_host(the one in which operation is running right now) and
           hosts can be defined in the yml like this
           current_host={{inventory_hostname}}
           hosts="{% for host in groups[<group name>] %}
           {{ hostvars[host]['private_ip'] }},{% endfor %}"

        '''
        self.current_host = self._validated_params('current_host')
        self.hosts = literal_eval(self._validated_params('hosts'))

    def append_host_name(self):
        brick_list = []
        for host, bricks in zip(self.hosts, self.bricks):
            for brick in bricks.strip('[]').split(','):
                brick_list.append(host + ':' + brick.strip())
        return brick_list

    def get_brick_list_of_all_hosts(self):
        '''
        This get the bricks of all the hosts in the pool.
        Expected to provide 'bricks' in the yml in the same
        order as that of the hosts.
        '''
        self.bricks = filter(None, [brick.strip() for brick in
                self._validated_params('bricks').split(';')])
        return ' '.join(brick_path for brick_path in
                self.append_host_name())

    def gluster_peer_ops(self):
        if self.action in ['probe', 'detach']:
            self.get_host_names()
            peers = [peer for peer in self.hosts
                    if peer not in self.current_host]
            for hostname in peers:
                rc, output, err = self.call_gluster_cmd('peer',
                        self.action, self.force, hostname)
        else:
            rc, output, err = self.call_gluster_cmd('peer', self.action)
            #This still doesn't print output to stdout sadly.
        self._get_output(rc, output, err)

    def get_volume_configs(self):
        options = ' '
        if self.module.params['replica'] == 'yes':
            options += ' replica %d ' % int(self._validated_params('replica_count'))
            arbiter_count = int(self.module.params['arbiter_count'])
            if arbiter_count:
                options += ' arbiter %d ' % arbiter_count
        if self.module.params['disperse'] == 'yes':
            disperce_count = int(self.module.params['disperse_count'])
            if disperce_count:
                options += ' disperse-data %d ' % disperce_count
            else:
                options += ' disperse '
            redundancy = int(self.module.params['redundancy_count'])
            if redundancy:
                options += ' redundancy %d ' % redundancy
        options += ' transport ' + self._validated_params('transport')
        return (options + ' ')


    def gluster_volume_ops(self):
        option_str = ''
        if self.action in ['delete', 'set']:
            self.force = ''
        volume = self._validated_params('volume')
        if self.action == 'create':
            self.get_host_names()
            option_str = self.get_volume_configs()
            option_str += self.get_brick_list_of_all_hosts()
        if self.action == 'set':
            key = self._validated_params('key')
            value = self._validated_params('value')
            option_str = ' '.join(key + ' ' +  value)
        rc, output, err = self.call_gluster_cmd('volume', self.action,
                                               volume, option_str, self.force)
        self._get_output(rc, output, err)

    def call_gluster_cmd(self, *args, **kwargs):
        params = ' '.join(opt for opt in args)
        key_value_pair = ' '.join(' %s %s ' % (key, value)
                for key, value in kwargs)
        return self._run_command('gluster', ' ' + params + ' ' + key_value_pair)

    def _get_output(self, rc, output, err):
        if not rc:
            self.module.exit_json(stdout=output, changed=1)
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
            current_host=dict(),
            hosts=dict(),
            volume=dict(),
            bricks=dict(),
            force=dict(),
            key=dict(),
            value=dict(),
            replica=dict(),
            replica_count=dict(),
            arbiter_count=dict(),
            transport=dict(),
            disperse=dict(),
            disperse_count=dict(),
            redundancy_count=dict()
        ),
    )

    Gluster(module)
