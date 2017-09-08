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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

import sys
import re
from collections import OrderedDict
from ansible.module_utils.basic import *
from ast import literal_eval

class Peer(object):
    def __init__(self, module):
        self.module = module
        self.action = self._validated_params('action')

    def get_playbook_params(self, opt):
        return self.module.params[opt]

    def _validated_params(self, opt):
        value = self.get_playbook_params(opt)
        if value is None:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(rc=4,msg=msg)
        return value

    def get_host_names(self):
        '''
           Something like this can be used in the playbook:
           hosts="{% for host in groups[<group name>] %}
           {{ hostvars[host]['private_ip'] }},{% endfor %}"
        '''
        hosts = literal_eval(self._validated_params('hosts'))
        current_host = self._validated_params('master')
        try:
            hosts.remove(current_host)
        except:
            pass
        return hosts

    def gluster_peer_ops(self):
        hosts = self.get_host_names()
        force = 'force' if self.module.params.get('force') == 'yes' else ''
        if self.action == 'probe':
            hosts = self.get_to_be_probed_hosts(hosts)
        cmd = []
        if hosts:
            for hostname in hosts:
                cmd.append(' peer ' + self.action + ' ' + ' ' +
                        hostname + ' ' + force)
        return cmd

    def get_to_be_probed_hosts(self, hosts):
        rc, output, err = self.module.run_command(
                "gluster pool list")
        peers_in_cluster = [line.split('\t')[1].strip() for
                line in filter(None, output.split('\n')[1:])]
        try:
            peers_in_cluster.remove('localhost')
        except:
            pass
        hosts_to_be_probed = [host for host in hosts if host not in
                peers_in_cluster]
        return hosts_to_be_probed


    def call_peer_commands(self, cmds):
        errors = []
        for cmd in cmds:
            rc, out, err = pops._run_command('gluster', cmd)
            if rc:
                errors.append(err)
        return errors

    def get_output(self, errors):
        if not errors:
            self.module.exit_json(rc=0, changed=1)
        else:
            self.module.fail_json(rc=1, msg='\n'.join(errors))

    def _run_command(self, op, opts):
        cmd = self.module.get_bin_path(op, True) + opts + ' --mode=script'
        return self.module.run_command(cmd)

if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=True),
            master=dict(),
            hosts=dict(),
            force=dict(),
        ),
    )

    pops = Peer(module)
    cmds = pops.gluster_peer_ops()
    errors = pops.call_peer_commands(cmds)
    pops.get_output(errors)
