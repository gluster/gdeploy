#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (c) 2016, Nandaja Varma <nandaja.varma@gmail.com>
#
#
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

import json, os

class Kubectl:

    def __init__(self, module):
        self.module = module
        self.action = self._validated_params('action')


    def run(self):
        action_func = {
                        'create': self.oc_create,
                        'get': self.oc_get,
                        'delete': self.oc_delete,
                        'exec': self.oc_exec,
                        'stop': self.oc_stop,
                        'run': self.oc_run
                      }.get(self.action)

        try:
            return action_func()
        except:
            msg = "No method found for given action"
            self.get_output(rc=3, out=msg, err=msg)


    def oc_create(self):
        filename = self.module.params['filename']
        filetype = self.module.params['filetype'] or ''
        if filetype == 'template' and filename:
            val = self.module.params['variable']
            if val and val.strip() and re.match('.*=.*', val):
                v = ' -v %s ' % val
            else:
                v = ' '
            template = os.path.basename(filename).split('-')[0]
            return "cat {0} | oc create -f -; oc process {1} {2} | oc "\
                                "create -f -".format(filename,template,  v)
        if filename:
            return "cat %s | oc %s -f -" % (filename, self.action)

    def oc_run(self):
        name = self._validated_params('name')
        image = self._validated_params('image')
        return "oc %s %s --image=%s" % (self.action,
                name, image)

    def oc_exec(self):
        pod = self._validated_params('pod')
        container = self.module.params['container']
        c_opts = '-c %s' % container if container else ''
        command = self._validated_params('command')
        if ',' in command:
            command = command.replace(',',';')
        return "oc %s %s %s %s" %(self.action, pod, c_opts,
                command)

    def oc_delete(self):
        filename = self.module.params['filename']
        if filename and filename.strip():
            return "cat %s | oc %s -f -" % (filename, self.action)
        ropts = self._validated_params('type') or ''
        label = self.module.params['label'] or ''
        if label and label.strip():
            return "oc %s %s -l %s" % (self.action, ropts, label)
        name = self.module.params['name']
        name = ' '.join(name.split(',')) if name else '--all'
        return "oc %s %s %s" % (self.action, ropts, name)


    def oc_stop(self):
        filename = self.module.params['filename']
        if filename:
            return "cat %s | oc %s -f -" % (filename, self.action)
        ropts = self._validated_params('type') or ''
        uid = self.module.params['uid'] or ''
        if uid:
            return "oc %s %s %s" % (self.action, ropts, uid)
        label = self.module.params['label'] or ''
        if label:
            return "oc %s %s -l %s" % (self.action, ropts, label)
        name = self.module.params['name']
        name = ' '.join(name.split(',')) if name else '--all'
        return "oc %s %s %s" % (self.action, ropts, name)



    def oc_get(self):
        res_type = self.module.params['type']
        ropts = res_type if res_type else ''

        name = self.module.params['name']
        nopts = name if (name and ropts) else ''

        filename = self.module.params['filename']
        fopts = '-f %s' % filename if (filename and not ropts) else ''

        output = self.module.params['output']
        o_opts = '-o %s' % output if output else ''

        options = list(filter(None, [ropts, nopts, fopts, o_opts]))
        return 'oc {0} {1}'.format(self.action, ' '.join(options))

    def _validated_params(self, opt):
        value = self.module.params[opt]
        if value is None or not value.strip():
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(msg=msg)
        return value

    def get_output(self, rc=0, out=None, err=None):
        if rc:
            self.module.fail_json(msg=err, rc=rc, err=err, out=out)
        else:
            self.module.exit_json(changed=1, msg=json.dumps(out))

def main():
    module = AnsibleModule(
            argument_spec = dict(
                action          = dict(required=True, choices=["create",
                                    "stop", "run", "exec", "get", "delete"]),
                name            = dict(required=False),
                type            = dict(required=False),
                filetype        = dict(required=False),
                filename        = dict(required=False),
                label           = dict(required=False),
                uid             = dict(required=False),
                container       = dict(required=False),
                command         = dict(required=False),
                pod             = dict(required=False),
                output          = dict(required=False),
                image           = dict(required=False),
                variable        = dict(required=False),
                ),
            supports_check_mode = True
            )


    kube = Kubectl(module)
    cmd = kube.run()
    rc, out, err = module.run_command(cmd, use_unsafe_shell=True)
    kube.get_output(rc, out, err)



from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
