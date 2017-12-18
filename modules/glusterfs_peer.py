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
        self.state = self._validated_params('state')

    def _validated_params(self, opt):
        if self.module.params[opt] is None:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(rc=4,msg=msg)
        return self.module.params[opt]

    def get_nodes(self):
        '''
           Something like this can be used in the playbook:
           hosts="{% for host in groups[<group name>] %}
           {{ hostvars[host]['private_ip'] }},{% endfor %}"
        '''
        nodes = literal_eval(self._validated_params('nodes'))
        if nodes[0] is None:
            # Found a list with None as its first element
            self.module.exit_json(rc=1, msg="No nodes found, provide atleast "
                                  "one node.")
        return nodes

    def gluster_peer_ops(self):
        nodes = self.get_nodes()
        force = 'force' if self.module.params.get('force') == 'yes' else ''
        if self.state == 'present':
            nodes = self.get_to_be_probed_hosts(nodes)
            action = 'probe'
        elif self.state == 'absent':
            action = 'detach'
        cmd = []
        for node in nodes:
            cmd.append(' peer ' + action + ' ' + node + ' ' + force)
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
            force=dict(choices=["yes", "no"]),
            nodes=dict(),
            state=dict(required=True, choices=["absent", "present"]),
        ),
    )

    pops = Peer(module)
    cmds = pops.gluster_peer_ops()
    errors = pops.call_peer_commands(cmds)
    pops.get_output(errors)
