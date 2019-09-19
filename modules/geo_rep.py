#!/usr/bin/python3
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
        slavevol = self.check_pool_exclusiveness(mastervol, slavevol)
        if self.action in ['delete', 'config']:
            force = ''
        else:
            force = self._validated_params('force')
            force = 'force' if force == 'yes' else ' '
        options = 'no-verify' if self.action == 'create' \
            else self.config_georep()
        if type(options) is list:
            for opt in options:
                rc, output, err = self.call_gluster_cmd('volume',
                                                        'geo-replication',
                                                        mastervol, slavevol,
                                                        self.action, opt,
                                                        force)
        else:
            rc, output, err = self.call_gluster_cmd('volume',
                                                    'geo-replication',
                                                    mastervol, slavevol,
                                                    self.action, options,
                                                    force)
        self._get_output(rc, output, err)
        if self.action in ['stop', 'delete'] and self.user == 'root':
            self.user = 'geoaccount'
            rc, output, err = self.call_gluster_cmd('volume', 'geo-replication',
                    mastervol, slavevol.replace('root', 'geoaccount'),
                    self.action, options, force)
            self._get_output(rc, output, err)

    def config_georep(self):
        if self.action != 'config':
            return ''
        options = ['gluster_log_file', 'gluster_log_level', 'log_file',
                   'log_level', 'changelog_log_level', 'ssh_command',
                   'rsync_command', 'use_tarssh', 'volume_id', 'timeout',
                   'sync_jobs', 'ignore_deletes', 'checkpoint', 'sync_acls',
                   'sync_xattrs', 'log_rsync_performance', 'rsync_options',
                   'use_meta_volume', 'meta_volume_mnt']
        configs = []
        for opt in options:
           value = self._validated_params(opt)
           if value:
               if value == 'reset':
                   configs.append("'!" + opt.replace('_', '-') + "'")
               configs.append(opt.replace('_', '-') + ' ' + value)
        if configs:
            return configs
        value = self._validated_params('config')
        op = self._validated_params('op')
        return value + ' ' + op

    def check_pool_exclusiveness(self, mastervol, slavevol):
        rc, output, err = self.module.run_command(
                "gluster pool list")
        peers_in_cluster = [line.split('\t')[1].strip() for
                            line in list(filter(None, output.split('\n')[1:]))]
        val_group = re.search("(.*):(.*)", slavevol)
        if not val_group:
            self.module.fail_json(msg="Slave volume in Unknown format. "\
                    "Correct format: <hostname>:<volume name>")
        if val_group.group(1) in peers_in_cluster:
            self.module.fail_json(msg="slave volume is in the trusted " \
                    "storage pool of master")
        self.user = 'root' if self.module.params['georepuser'] is None \
            else self.module.params['georepuser']
        return self.user + '@' + val_group.group(1) + '::' + val_group.group(2)

    def call_gluster_cmd(self, *args, **kwargs):
        params = ' '.join(opt for opt in args)
        key_value_pair = ' '.join(' %s %s ' % (key, value)
                for key, value in kwargs)
        return self._run_command('gluster', ' ' + params + ' ' + key_value_pair)

    def _get_output(self, rc, output, err):
        carryon = True if self.action in  ['stop',
                'delete', 'resume'] else False
        changed = 0 if (carryon and rc) else 1
        if self.action in ['stop', 'delete'] and (
                self.user == 'root' and changed == 0):
            return
        if not rc or carryon:
            self.module.exit_json(stdout=output, changed=changed)
        else:
            self.module.fail_json(msg=err)

    def _run_command(self, op, opts):
        cmd = self.module.get_bin_path(op, True) + opts
        return self.module.run_command(cmd)

if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=True, choices=['create', 'start',
                'stop', 'delete', 'pause', 'resume', 'config']),
            mastervol=dict(),
            slavevol=dict(),
            force=dict(),
            georepuser=dict(),
            gluster_log_file=dict(),
            gluster_log_level=dict(),
            log_file=dict(),
            log_level=dict(),
            changelog_log_level=dict(),
            ssh_command=dict(),
            rsync_command=dict(),
            use_tarssh=dict(),
            volume_id=dict(),
            timeout=dict(),
            sync_jobs=dict(),
            ignore_deletes=dict(),
            checkpoint=dict(),
            sync_acls=dict(),
            sync_xattrs=dict(),
            log_rsync_performance=dict(),
            rsync_options=dict(),
            use_meta_volume=dict(),
            meta_volume_mnt=dict()
        ),
    )

    GeoRep(module)
