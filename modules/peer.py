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
import re
from ansible.module_utils.basic import *
from ast import literal_eval

class Peer(object):
    def __init__(self, module):
        self.module = module
        self.action = self._validated_params('action')
        self.gluster_peer_ops()

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
        self.hosts = literal_eval(self._validated_params('hosts'))

    def gluster_peer_ops(self):
        self.get_host_names()
        if self.action == 'probe':
            if not self.module.check_mode:
                self.hosts = self.get_to_be_probed_hosts()
        self.current_host = self._validated_params('current_host')
        try:
            self.hosts.remove(self.current_host)
        except:
            pass
        self.force = 'force' if self.module.params.get('force') == 'yes' else ''
        if self.hosts:
            rc, output, err = [0, 0, 0]
            for hostname in self.hosts:
                rc, output, err = self.call_gluster_cmd('peer',
                        self.action, hostname, self.force)
            self._get_output(rc, output, err)
        else:
            self.module.exit_json()

    def get_to_be_probed_hosts(self):
        rc, output, err = self.module.run_command(
                "gluster pool list")
        peers_in_cluster = [line.split('\t')[1].strip() for
                line in filter(None, output.split('\n')[1:])]
        try:
            peers_in_cluster.remove('localhost')
        except:
            pass
        hosts_to_be_probed = [host for host in self.hosts if host not in
                peers_in_cluster]
        return hosts_to_be_probed


    def call_gluster_cmd(self, *args, **kwargs):
        params = ' '.join(opt for opt in args)
        key_value_pair = ' '.join(' %s %s ' % (key, value)
                for key, value in kwargs)
        return self._run_command('gluster', ' ' + params + ' ' + key_value_pair)

    def _get_output(self, rc, output, err):
        changed = 0 if rc else 1
        if not rc:
            self.module.exit_json(rc=rc, stdout=output, changed=changed)
        else:
            self.module.fail_json(rc=rc, msg=err)

    def _run_command(self, op, opts):
        cmd = self.module.get_bin_path(op, True) + opts + ' --mode=script'
        if self.module.check_mode == True:
            self.module.fail_json(msg=cmd, rc=0, output=cmd)
        return self.module.run_command(cmd)


if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=True),
            current_host=dict(),
            hosts=dict(),
            force=dict(),
        ),
        supports_check_mode=True
    )

    Peer(module)
