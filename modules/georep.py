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
from collections import OrderedDict
from ansible.module_utils.basic import *
from ast import literal_eval

class GeoRep(object):
    def __init__(self, module):
        self.module = module
        self.action = self._validated_params('action')
        self.gluster_georep_ops()

    def get_playbook_params(self, opt):
        return self.module.params[opt]

    def _validated_params(self, opt):
        value = self.get_playbook_params(opt)
        if value is None:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(msg=msg)
        return value

    def gluster_georep_ops(self):
        mastervol = self._validated_params('mastervol')
        slavevol = self._validated_params('slavevol')
        force = self._validated_params('force')
        force = 'force' if force == 'yes' else ' '
        push_pem = 'push-pem' if self.action == 'create' else ' '
        rc, output, err = self.call_gluster_cmd('volume', 'geo-replication',
                mastervol, slavevol, self.action, push_pem, force)
        self._get_output(rc, output, err)

    def call_gluster_cmd(self, *args, **kwargs):
        params = ' '.join(opt for opt in args)
        key_value_pair = ' '.join(' %s %s ' % (key, value)
                for key, value in kwargs)
        return self._run_command('gluster', ' ' + params + ' ' + key_value_pair)

    def _get_output(self, rc, output, err):
        carryon = True if self.action in  ['stop',
                'delete', 'detach'] else False
        changed = 0 if (carryon and rc) else 1
        if not rc or carryon:
            self.module.exit_json(stdout=output, changed=changed)
        else:
            self.module.fail_json(msg=err)

    def _run_command(self, op, opts):
        cmd = self.module.get_bin_path(op, True) + opts + ' --mode=script'
        return self.module.run_command(cmd)

if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=True, choices=['create', 'start']),
            mastervol=dict(),
            slavevol=dict(),
            force=dict(),
        ),
    )

    GeoRep(module)
