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

'''

EXAMPLES = '''
---

'''

import sys
import re
from collections import OrderedDict
from ansible.module_utils.basic import *
from ast import literal_eval

class Quota(object):
    def __init__(self, module):
        self.module = module
        self.action = self._validated_params('action')
        self.volume = self._validated_params('volume')
        self.gluster_quota_opts()

    def get_playbook_params(self, opt):
        return self.module.params[opt]

    def _validated_params(self, opt):
        value = self.get_playbook_params(opt)
        if value is None:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(rc=1,msg=msg)
        return value


    def gluster_quota_opts(self):

        option_str = None
        if self.action in ['enable', 'disable']:
            option_str = self.action

        action_func =  {
                         'default_soft_limit': self.quota_default_soft_limit,
                         'limit_usage': self.quota_limit_usage,
                         'limit_objects': self.quota_limit_objects,
                        }.get(self.action)


        if self.action in ['remove', 'remove_objects']:
            action_func = self.quota_remove_action

        if self.action in ['alert_time', 'soft_timeout', 'hard_timeout']:
            action_func = self.quota_time_bounds

        if action_func:
            option_str = action_func()

        if not option_str:
            self.fail_json(rc=1,msg="Unknown action")

        rc, out, err = self.call_gluster_cmd('volume', 'quota',
            self.volume, option_str)
        self._get_output(rc, out, err)

    def quota_default_soft_limit(self):
        percent = self._validated_params('percent')
        return ' default-soft-limit %s ' % percent


    def quota_limit_usage(self):
        path = self._validated_params('path')
        size = self._validated_params('size')
        percent = self.get_playbook_params('percent')
        percent = ' ' if not percent else percent
        return ' limit-usage %s %s %s ' %(path, size, percent)

    def quota_limit_objects(self):
        path = self._validated_params('path')
        number = self._validated_params('number')
        percent = self.get_playbook_params('percent')
        percent = ' ' if not percent else percent
        return ' limit-objects %s %s %s ' %(path, number, percent)

    def quota_remove_action(self):
        path = self._validated_params('path')
        return ' %s  %s ' %(self.action.replace('_', '-'), path)

    def quota_time_bounds(self):
        time = self._validated_params('time')
        return ' %s  %s ' %(self.action.replace('_', '-'), time.lower())

    def call_gluster_cmd(self, *args, **kwargs):
        params = ' '.join(opt for opt in args)
        key_value_pair = ' '.join(' %s %s ' % (key, value)
                for key, value in kwargs)
        return self._run_command('gluster', ' ' + params + ' ' + key_value_pair)

    def _get_output(self, rc, output, err):
        if not rc:
            self.module.exit_json(rc=rc, stdout=output, changed=1)
        else:
            self.module.fail_json(msg=err,rc=rc)

    def _run_command(self, op, opts):
        cmd = self.module.get_bin_path(op, True) + opts + ' --mode=script'
        return self.module.run_command(cmd)

if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=True),
            volume=dict(required=True),
            path=dict(),
            size=dict(),
            number=dict(),
            percent=dict(),
            time=dict()
        ),
    )

    Quota(module)
