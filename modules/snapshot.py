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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.

import sys
from collections import OrderedDict
from ansible.module_utils.basic import *
from ast import literal_eval


class Snapshot(object):
    def __init__(self, module):
        self.module = module
        self.action = self._validated_params('action')
        self.force = 'force' if self.module.params.get(
            'force') == 'yes' else ''
        if self.action == 'config':
            self.snapshot_config()
        self.gluster_snapshot_ops()

    def get_playbook_params(self, opt):
        return self.module.params[opt]

    def _validated_params(self, opt):
        value = self.get_playbook_params(opt)
        if value is None:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(msg=msg)
        return value

    def create_params_dict(self, param_list):
        return OrderedDict((param, self.get_playbook_params(param))
                           for param in param_list)

    def gluster_snapshot_ops(self):
        option_str = ' '
        direct_value_params = {'create':  ['snapname', 'volume',
                                           'options'],
                               'clone': ['snapname', 'clonename'],
                               'restore': ['snapname'],
                               'delete': ['snapname'],
                               'activate': ['snapname'],
                               'deactivate': ['snapname']
                               }[self.action]
        direct_param_dict = self.create_params_dict(direct_value_params)
        for params in direct_value_params:
            if direct_param_dict[params]:
                option_str += ' %s ' % direct_param_dict[params]

        try:
            keyword_needed_params = {'create': ['description'],
                                     'delete': ['volume']
                                     }[self.action]
            keyword_param_dict = self.create_params_dict(keyword_needed_params)
            for params in keyword_needed_params:
                if keyword_param_dict[params]:
                    if params == 'description':
                        option_str += "%s '%s' " % (params,
                                                    keyword_param_dict[params])
                    else:
                        option_str += '%s %s ' % (params.replace('_', '-'),
                                                  keyword_param_dict[params])
        except:
            pass

        if self.action not in ['create', 'activate']:
            self.force = ''

        rc, output, err = self.call_gluster_cmd('snapshot', self.action,
                                                option_str, self.force)
        self._get_output(rc, output, err)

    def snapshot_config(self):
        option_str = []
        max_hard_limit = self.module.params['snap_max_hard_limit']
        if max_hard_limit:
            option_str.append('snap-max-hard-limit %s ' % max_hard_limit)
        max_soft_limit = self.module.params['snap_max_soft_limit']
        if max_soft_limit:
            option_str.append('snap-max-soft-limit %s ' % max_soft_limit)
        auto_delete = self.module.params['auto_delete']
        if auto_delete:
            option_str.append('auto-delete %s ' % auto_delete)
        act_on_create = self.module.params['activate_on_create']
        if act_on_create:
            option_str.append('activate-on-create %s ' % act_on_create)
        for option in option_str:
            rc, output, err = self.call_gluster_cmd('snapshot', self.action,
                                                    option, self.force)
        self._get_output(rc, output, err)

    def call_gluster_cmd(self, *args, **kwargs):
        params = ' '.join(opt for opt in args)
        key_value_pair = ' '.join(' %s %s ' % (key, value)
                                  for key, value in kwargs)
        return self._run_command('gluster', ' ' + params + ' ' + key_value_pair)

    def _get_output(self, rc, output, err):
        carryon = True if self.action in ['stop',
                                          'delete', 'deactivate'] else False
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
            action=dict(required=True),
            volume=dict(),
            force=dict(),
            snapname=dict(),
            description=dict(),
            options=dict(),
            clonename=dict(),
            snap_max_hard_limit=dict(),
            snap_max_soft_limit=dict(),
            auto_delete=dict(),
            activate_on_create=dict()
        ),
    )

    Snapshot(module)
