#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Ansible module to create or remove a Logical Volume.
(c) 2015 Nandaja Varma <nvarma@redhat.com>, Ashmitha Ambastha <asambast@redhat.com>
This file is part of Ansible
Ansible is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Ansible is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Ansible. If not, see <http://www.gnu.org/licenses/>.
"""
ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'supported_by': 'community',
    'status': ['preview']
}
DOCUMENTATION = '''
---
authors: Nandaja Varma, Ashmitha Ambastha
module: lv
short_description: Create, resize, change, reduce, convert, extend, rename,
                   and remove Logical Volumes and Thin Pools.
description:
    - Creates, resizes, changes, reduces, converts, extends, renames, and removes
      Logical Volumes and Thin Pools of remote hosts
options:
    action:
        required: true
        choices: [create,resize,change,reduce,convert,extend, rename,remove]
        description: Specifies the LV operation that is to be executed,
                     can be create, convert, change or remove .
   lvname:
        required: false
        description: Specifies the name of the LV to be created or removed.
   poolname:
        required: false
        description: Specifies the name of the pool that is to be associated
                     with the LV or is to be created or is to be changed.
   vgname:
        required: true
        description: Desired volume group names to which the LVs are to be
                     associated or with which the LVs are associated.
   lvtype:
        required: true
        action: create
        choices: [thin, thick, virtual]
        description: Required with the create action of the LV module.
                     With the option thick, the module creates a metadata LV,
                     With the option thin, the module creates a thin pool and
                     with hte option virtual, logical volumes for the pool will
                     be created.
    compute:
        required: true
        action: create
        choice: [rhs]
        description: This is an RHS specific computation for LV creation.
                     Pool size and metadata LV size will be calculated as per
                     RHS specifics. Additional modules has to be added if any
                     other specifics is needed.
    thinpool:
        required: true
        action: convert
        desciption: Required with the action convert, this can be used to
                    associate metadata LVs with thin pools. thinpool name
                    should be in the format vgname/lvname
    poolmetadata:
        required: true
        action: convert
        description: This specifies the name of the metadata LV that is to
                     be associated with the thinpool described by the
                     previos option
    poolmetadataspare:
        required: false
        choices: [yes, no]
        description: Controls  creation  and  maintanence  of pool metadata
                     spare logical volume that will be used for automated
                     pool recovery. Default is yes.
    zero:
        required: false
        choices: [y, n]
        description: Set zeroing mode for thin pool. To be used with the
                     change action of the logical volume.
'''

EXAMPLES = '''
    Create logical volume named metadata
    lv: action=create
        lvname=metadata
        lvtype=thinpool
        vgname=RHS_vg1
    Create a thin pool
    lv: action=create
        lvname=RHS_pool1
        lvtype=thin
        vgname=RHS_vg1
    Convert the logical volume
    lv: action=convert
        thinpool='RHS_vg1/RHS_pool1
        poolmetadata='RHS_vg1'/'metadata' poolmetadataspare=n
        vgname=RHS_vg1
    Create logical volume for the pools
    lv: action=create poolname='RHS_pool1' lvtype="virtual"
        compute=rhs
        vgname=RHS_vg1
        lvname=RHS_lv1
    Change the attributes of the logical volume
    lv: action=change
        zero=n
        vgname='RHS_vg1'
        poolname='RHS_pool1'
    Remove logical volumes
    lv: action=remove
        vgname=RHS_vg1
        lvname=RHS_lv1
---
'''

from ansible.module_utils.basic import *
import json
from ast import literal_eval
from math import floor
error = False


class LvOps(object):

    def __init__(self, module):
        self.module = module
        self.action = self.validated_params('action')
        self.vgname = self.validated_params('vgname')
        self.lvname = self.validated_params('lvname')
        if self.action not in ['rename', 'remove','resize','change']:
            self.pvname = self.validated_params('pvname')

    def lv_action(self):
        cmd = {'create': self.create,
               'change': self.change,
               'extend': self.extend,
               'resize': self.resize,
               'reduce': self.reduce,
               'rename': self.rename,
               'remove': self.remove
               }[self.action]()
        return cmd

    def get_output(self, rc, output, err):
        if not rc:
            self.module.exit_json(rc=rc, stdout=output, changed=1)
        else:
            self.module.fail_json(rc=rc, msg=err)

    def metadata_compute(self):
        #This is an RHS specific computation method for performance
        #improvements. User can choose not to use it by providing
        # metadatasize and poolsize in the playbook.
        metadatasize = 0
        global error
        self.vg_presence_check(self.vgname)
        option = " --noheading --units m  -o vg_size %s" % self.vgname
        rc, vg_size, err = self.run_command('vgs', option)
        if not rc:
            vg_size = list(set(filter(
                                None, vg_size.split(' '))))[0]
            vg_size = floor(float(vg_size.strip(' m\t\r\n')) - 4)
            KB_PER_GB = 1048576
            if vg_size > 1000000:
                METADATA_SIZE_GB = 16
                metadatasize = floor(METADATA_SIZE_GB * KB_PER_GB)
            else:
                METADATA_SIZE_MB = vg_size / 200
                metadatasize = floor(floor(METADATA_SIZE_MB) * 1024)
            self.vg_size = vg_size
            return metadatasize
        self.module.fail_json(msg=err, rc=rc)


    def poolsize_compute(self):
        metadatasize = self.metadata_compute()
        pool_sz = floor(self.vg_size * 1024) - metadatasize
        snapshot_space = self.module.params['snapshot_reserve'] or 0
        pool_sz -= (pool_sz * int(snapshot_space) / 100)
        return pool_sz

    def validated_params(self, opt):
        value = self.module.params[opt]
        if value is None or not value.strip(' '):
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(msg=msg)
        return value

    def run_command(self, op, options=""):
        cmd = self.module.get_bin_path(op, True) + options
        return self.module.run_command(cmd)

    def create_thick_pool(self):
        compute_type = self.module.params['compute'] or ''
        compute_func = getattr(self, compute_type, None)
        lvname = self.validated_params('lvname')
        self.lv_presence_check(lvname)
        sop = ''
        try:
            size = str(compute_func()) + 'K'
        except:
            size = self.module.params.get('size')
        if not size:
            extent = self.module.params.get('extent') or '100%FREE'
            sop = ' -l %s' % extent
        else:
            sop = ' -L %s' % size
        pvname = self.module.params.get('pvname') or ''
        opts = ' -Wn %s -n %s %s %s' %(sop, lvname, self.vgname, pvname)
        return opts


    def create_thin_pool(self):
        lvcreate = {}
        lvcreate['chunksize'] = self.module.params['chunksize']
        lvcreate['poolmetadatasize'] = self.module.params[
                'poolmetadatasize'] or ''
        poolname = self.validated_params('poolname')
        self.lv_presence_check(poolname)
        lvcreate['thinpool'] = self.get_vg_appended_name(poolname)
        lvcreate['size'] = self.module.params['size'] or ''
        cmd = self.parse_playbook_data(lvcreate)
        if not lvcreate['size']:
            extent = self.module.params.get('extent') or '100%FREE'
            extcmd = ' -l %s'%extent
            opts = ' -Wn %s %s' %(extcmd, cmd)
        else:
            opts = ' -Wn %s' %cmd
        return opts

    def create_thin_lv(self):
        lvcreate = {}
        lvcreate['virtualsize'] = self.module.params[
                'virtualsize'] or (str(self.poolsize_compute()) + 'K')
        lvname = self.validated_params('lvname')
        self.lv_presence_check(lvname)
        lvcreate['name'] = lvname
        poolname = self.get_vg_appended_name(self.validated_params('poolname'))
        cmd = self.parse_playbook_data(lvcreate)
        return (cmd + ' -T ' + poolname)

    def vg_presence_check(self, vg):
        rc, out, err = self.run_command('vgdisplay', ' ' + vg)
        if rc:
            self.module.fail_json(rc=rc, msg="%s Volume Group Doesn't Exists!" % vg)
        return rc

    def lv_presence_check(self, lvname):
        rc, out, err = self.run_command('lvdisplay', ' '+ self.vgname +
                '/' + lvname)
        ret = 0
        if self.action == 'create' and not rc:
            self.module.exit_json(changed=0, msg="%s Logical Volume Exists!"
                    % lvname)
        elif self.action in ['convert', 'change', 'remove'] and rc:
            self.module.exit_json(changed=0, msg="%s Logical Volume Doesn't "\
                    "Exists!" % lvname)
        else:
            ret = 1
        return ret

    def rename(self):
        args= " "
        args += '%s/%s' % (self.vgname,self.lvname)
        new_name= self.module.params['new_name']
        args += " "+ str(new_name)
        return args

    def resize(self):
        args= " "
        force= self.module.params['force']
        if force == 'y':
            args += " -f "
        nofsck = self.module.params['nofsck']
        if nofsck=='y':
            args += " -n "
        resizefs = self.module.params['resizefs']
        if resizefs=='y':
            args += " -r "
        size = self.module.params['size']
        args += "-L" + size + " "
        stripe = self.module.params['stripe']
        if stripe=='y':
            args += " -i "
        stripesize = self.module.params['stripesize']
        if stripesize:
            args += " -I " + stripesize
        args += '%s/%s' % (self.vgname,self.lvname)
        return args

    def reduce(self):
        args= " "
        force = self.module.params['force']
        if force == 'y':
            args += " -f "
        sop = ''
        try:
            size = str(compute_func()) + 'K'
        except:
            size = self.module.params.get('size')
        if not size:
            extent = self.module.params.get('extent') or '100%FREE'
            sop = ' -l %s' % extent
        else:
            sop = ' -L %s' % size
        nofsck = self.module.params['nofsck']
        if nofsck=='y':
            args += "-n "
        resizefs = self.module.params['resizefs']
        if resizefs=='y':
            args += "-r "
        args += '%s/%s %s' % (self.vgname,self.lvname,self.pvname)
        return sop + args

    def extend(self):
        args= " "
        force = self.module.params['force']
        if force == 'y':
            args += " -f "
        sop = ''
        try:
            size = str(compute_func()) + 'K'
        except:
            size = self.module.params.get('size')
        if not size:
            extent = self.module.params.get('extent') or '100%FREE'
            sop = ' -l %s' % extent
        else:
            sop = ' -L %s' % size
        nofsck = self.module.params['nofsck']
        if nofsck=='y':
            args += "-n "
        resizefs = self.module.params['resizefs']
        if resizefs=='y':
            args += "-r "
        args += '/dev/%s/%s %s' % (self.vgname,self.lvname,self.pvname)
        return sop + args

    def create(self):
        args = " "
        cachemode = self.module.params['cachemode']
        if cachemode in ["writethrough","writeback","passthrough"]:
            args += "--cachemode " + cachemode
        poolmetadataspare = self.module.params["poolmetadataspare"]
        if poolmetadataspare == 'y':
            args += "--poolmetadataspare " + str(poolmetadataspare)
        stripesize = self.module.params['stripesize']
        if stripesize:
            args += "-I " + stripesize
        thin = self.module.params['thin']
        if thin:
            args += "-T "
        # thinpool = self.module.params['thinpool']
        # if thinpool :
        #     args += "--thinpool " + self.vgname + "/" + thinpool
        virtualsize = self.module.params['virtualsize']
        args += " -V " + virtualsize + " "
        wipesignature = self.module.params['wipesignature']
        if wipesignature == 'y':
            args += "-W " + wipesignature
        zero = self.module.params['zero']
        if zero:
            args += " -Z y "
        self.lvtype = self.validated_params('lvtype')
        options = {'thick': self.create_thick_pool,
                   'thinpool':  self.create_thin_pool,
                   'thinlv': self.create_thin_lv
                   }[self.lvtype]()
                   # 'virtual': ' -V %sK -T /dev/%s/%s -n %s'
                   # % (pool_sz, self.vgname, poolname, lvname)
                   # }[self.lvtype]
        # self.module.exit_json(rc=1,msg= "Debug output:\n" + options + " " + args)
        return options + " " + args

    def parse_playbook_data(self, dictionary, cmd=''):
        for key, value in dictionary.iteritems():
            if value and str(value).strip(' '):
                cmd += ' --%s %s ' % (key, value)
        return cmd

    def get_vg_appended_name(self, lv):
        if not lv or not lv.strip():
            return ''
        if not '/' in lv:
            return self.vgname + '/' + lv
        return lv

    def change(self):
        args = " "
        errorwhenfull = self.module.params['errorwhenfull']
        if errorwhenfull == 'n':
            args += "--errorwhenfull " + errorwhenfull
        permission = self.module.params['permission']
        if permission in ["r","rw"]:
            args += " -p" + permission
        poolname = self.validated_params('lvname')
        self.lv_presence_check(poolname)
        poolname = self.get_vg_appended_name(poolname)
        zero = self.module.params['zero'] or 'n'
        # options = self.module.params['options']
        options = ' -Z %s %s/%s' % (zero, self.vgname, poolname)
        return options + " " + args

    def remove(self):
        lvname = self.validated_params('lvname')
        self.lv_presence_check(lvname)
        opt = ' -ff /dev/%s/%s' % (self.vgname, lvname)
        return opt


if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(choices=["create", "change", "resize",
                                "reduce","remove",'rename','extend']),
            lvname=dict(type='str'),
            lv=dict(),
            cachemode=dict(),
            cachepool=dict(),
            lvtype=dict(),
            pvname=dict(type='str'),
            vgname=dict(type='str'),
            new_name=dict(type='str'),
            thinpool=dict(),
            poolmetadata=dict(),
            poolmetadatasize=dict(),
            poolmetadataspare=dict(),
            poolname=dict(),
            zero=dict(),
            stripe=dict(),
            thin=dict(),
            options=dict(),
            compute=dict(),
            cache=dict(),
            disktype=dict(),
            wipesignature=dict(),
            diskcount=dict(),
            stripesize=dict(),
            chunksize=dict(),
            virtualsize=dict(),
            nofsck=dict(),
            resizefs=dict(),
            errorwhenfull=dict(),
            permission=dict(),
            size=dict(),
            extents=dict(),
            snapshot_reserve=dict(),
            force=dict()
        ),
    )

    lvops = LvOps(module)
    cmd = lvops.lv_action()
    rc, out, err = lvops.run_command('lv' + lvops.action, ' ' + cmd)
    lvops.get_output(rc, out, err)
