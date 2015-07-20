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

DOCUMENTATION = '''
---
module: gluster
short_description: Implementaion of GlusterFS
description:
    - A module to set-up a GlusterFS cluster by creating a TSP and
      creating volumes out of bricks. The host group on which
      playbooks will be written for this module should contain
      only one hostname which should be a part of the cluster
      and from which all the Gluster commands will be executed.
      This will make sure the commands are only run once.


options:
    commands:
        required: True
        choices: [peer, volume]
        description: Specifies if the operation is a peer operation or
                     volume operation. A peer operation does peer probe
                     and peer detach, whereas a volume operation does
                     volume create, delete, start, stop, add-brick and
                     remove-brick.
    action:
        required: True
        choices: [probe, detach] (If the command is peer)
                 [create, delete, start, stop, add-brick, remove-brick, set] (If
                 the command is volume)
        description: Specifies what exact action is to be done. Under peer
                     command, it can do probing and detaching. For volume
                     command, this can be create, delete, start, stop,
                     add-brick or remove-brick.
    volume:
        required: True (If command is volume)
        description: Specifies the name of the Gluster volume to be created.

    hosts:
        required: True
        description: The list of all the hosts that are to be a part of the
                     cluster.

    bricks:
        required: True (If command is volume and action is in [create,
                  add-brick, remove-brick])
        description: Specifies the bricks that constitutes the volume if
                     the action is volume create, the new bricks to be
                     added to a volume if the action is volume add-brick
                     and the bricks to be removed out of a volume
                     if the action is volume remove-brick. Format of each
                     brick should be hostname:brick_path.
    force:
        required: False
        description: Specifies if an operation is to be forced.
                     Applicable only to peer detach, volume { create, start,
                     stop, add-brick}

    key:
        required: True if command is volume and  action is set
        description: Set action sets options for the volume. Key
                     specifies which option is to be set

    value:
        required: True if command is volume and action is set
        description: Specifies the value to be set for the option
                     specified bt key.

    transport:
        required: False
        description: Specifies which transport type is to be used
                     while creating the volume. Default is tcp.

    replica:
        required: False
        description: Specifies the volume to be created is of type
                     replicate or not. Can also be used to change the
                     type while adding or removing bricks

    replica_count:
        required: True if replica is yes
        description: Specifies the replica count if the volume type is
                     to be replica

    arbiter_count:
        required: False
        description: If volume is of type replica, arbiter_count will
                     specify the number of bricks that will be configured
                     as arbiter node. If replica_count is 3 and arbiter_count
                     is 1, 3rd brick of the replica is automatically
                     configured as an arbiter node.

    disperse:
        required: False
        choices: [yes, no]
        descirption: Specifies if the volume is to be disperse or not

    disperse_count:
        required: False
        description: Specifies the number of disperse bricks. If not
        specified, the number of bricks specified is taken as the
        <count> value.

    redundancy_count:
        required: False
        description: Specifies the number of redundancy bricks. If
        if not specified and the volume if of type disperse,
        it's default value is computed so that it generates an
        optimal configuration.

    state:
        required: True if action is remove-brick for volume command
        choices: [start, stop, status, commit, force]
        description: Specifies the state of the volume if one or more
                     bricks are to be removed from the volume


'''

EXAMPLES = '''
---
#Creates a Trusted Storage Pool
  - gluster: command=peer action=probe
             hosts="{{ hosts }}"

# Detaches peers form a Trusted Storage Pool
 -  gluster: command=peer action=detach
             hosts="{{ hosts }}"

# Creates a volume
  - gluster: command=volume action=create
             volume="{{ volname }}"
             bricks='{% for host in hosts %}
             {{ hostvars[host]['mountpoints'] }};
             {% endfor %}'
             hosts="{{ hosts }}"
             transport=rdma
             replica=yes
             replica_count=3
             arbiter_count=1

# Sets options for volume
  - gluster: command=volume action=set
             volume="{{ volname }}"
             key=cluster.nufa value=on

'''

import sys
import re
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

    def get_host_names(self, required=False):
        '''
           Something like this can be used in the playbook:
           hosts="{% for host in groups[<group name>] %}
           {{ hostvars[host]['private_ip'] }},{% endfor %}"

        '''
        if not required:
            hosts = self.module.params['hosts']
            if hosts:
                self.hosts = literal_eval(hosts)
        else:
            self.hosts = literal_eval(self._validated_params('hosts'))

    def append_host_name(self):
        brick_list = []
        for host, bricks in zip(self.hosts, self.bricks):
            for brick in bricks.strip('[]').split(','):
                brick_list.append(host + ':' + brick.strip())
        return brick_list

    def get_brick_list_of_all_hosts(self):
        bricks = self._validated_params('bricks')
        if re.search(r'(.*):(.*)', bricks):
            return self.get_brick_list()
        '''
        If the bricks are not given in hostname:brickpath
        format, hostnames are to be provided as
        'hosts' in the playbook.
        This method gets the bricks of all the hosts in the pool.
        Expected to provide 'bricks' in the yml in the same
        order as that of the hosts.
        '''
        if not self.hosts:
            self.module.fail_json("Provide the bricks in hostname:brickpath " \
            " format or provide 'hosts' and 'bricks' should be of a format " \
                    " 'brick1, brick2; bricka, brickb' where brick1, brick2 " \
                    " belongs to host1 and brick1,brickb belongs to host2")
        self.bricks = filter(None, [brick.strip() for brick in
                                        bricks.split(';')])
        return ' '.join(brick_path for brick_path in
                self.append_host_name())

    def gluster_peer_ops(self):
        if self.action in ['probe', 'detach']:
            self.get_host_names(True)
            for hostname in self.hosts:
                rc, output, err = self.call_gluster_cmd('peer',
                        self.action, self.force, hostname)
        else:
            rc, output, err = self.call_gluster_cmd('peer', self.action)
            #This still doesn't print output to stdout sadly.
        self._get_output(rc, output, err)

    def get_volume_configs(self):
        options = ' '
        if self.module.params['replica'] == 'yes':
            options += ' replica %s ' % self._validated_params('replica_count')
            arbiter_count = self.module.params['arbiter_count']
            if arbiter_count:
                options += ' arbiter %s ' % arbiter_count
        if self.module.params['disperse'] == 'yes':
            disperce_count = self.module.params['disperse_count']
            if disperce_count:
                options += ' disperse-data %s ' % disperce_count
            else:
                options += ' disperse '
            redundancy = self.module.params['redundancy_count']
            if redundancy:
                options += ' redundancy %s ' % redundancy
        transport = self.module.params['transport']
        if transport:
            options += ' transport %s ' % transport
        return (options + ' ')

    def get_brick_list(self):
        return ' '.join(re.sub('[\[\]\']', '', brick.strip()) for brick in
                self._validated_params('bricks').split(',') if brick)

    def brick_ops(self):
        options = ' '
        if self.module.params['replica'] == 'yes':
            options += ' replica %s ' % self._validated_params('replica_count')
        new_bricks = self.get_brick_list()
        if self.action == 'remove-brick':
            return options + new_bricks + ' ' + self._validated_params('state')
        return options + new_bricks

    def gluster_volume_ops(self):
        option_str = ''
        if self.action in ['delete', 'set', 'remove-brick']:
            self.force = ''
        volume = self._validated_params('volume')
        if self.action == 'create':
            self.get_host_names()
            option_str = self.get_volume_configs()
            option_str += self.get_brick_list_of_all_hosts()
        if self.action == 'set':
            key = self._validated_params('key')
            value = self._validated_params('value')
            option_str = ' %s %s ' % (key, value)
        if re.search(r'(.*)brick$', self.action):
            option_str = self.brick_ops()
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
        cmd = self.module.get_bin_path(op, True) + opts + ' --mode=script'
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
            state=dict(),
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
