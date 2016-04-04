#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Ansible module to create or remove a Logical Volume.
(c) 2015 Nandaja Varma <nvarma@redhat.com>, Anusha Rao <arao@redhat.com>
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
DOCUMENTATION = '''
---
module: lv
short_description: Create or remove Logical Volumes and Thin Pools.
description:
    - Creates or removes n-number of Logical Volumes and Thin Pools on n-number
      of remote hosts

options:
    action:
        required: true
        choices: [create, change, convert, remove]
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
        required: true with action create
        choices: [thin, thick, virtual]
        description: Required with the create action of the LV module.
                     With the option thick, the module creates a metadata LV,
                     With the option thin, the module creates a thin pool and
                     with hte option virtual, logical volumes for the pool will
                     be created.

   compute:
        required: true with action create
        choice: [rhs]
        description: This is an RHS specific computation for LV creation.
                     Pool size and metadata LV size will be calculated as per
                     RHS specifics. Additional modules has to be added if any
                     other specifics is needed.


   thinpool:
        required: true with action convert
        desciption: Required with the action convert, this can be used to
                    associate metadata LVs with thin pools. thinpool name
                    should be in the format vgname/lvname

    poolmetadata:
        required: true with action convert
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
    lv: action=create lvname=metadata compute=rhs lvtype='thick'
        vgname='RHS_vg1'

    Create a thin pool
    lv: action=create lvname='RHS_pool1' lvtype='thin'
        compute=rhs vgname='RHS_vg1'

    Convert the logical volume
    lv: action=convert thinpool='RHS_vg1/RHS_pool1
        poolmetadata='RHS_vg1'/'metadata' poolmetadataspare=n
        vgname='RHS_vg1'

    Create logical volume for the pools
    lv: action=create poolname='RHS_pool1' lvtype="virtual"
        compute=rhs vgname=RHS_vg1 lvname='RHS_lv1'

    Change the attributes of the logical volume
    lv: action=change zero=n vgname='RHS_vg1' poolname='RHS_pool1'

    Remove logical volumes
    lv: action=remove
        vgname='RHS_vg1' lvname='RHS_lv1'

---
authors : Nandaja Varma, Anusha Rao
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

    def lv_action(self):
        cmd = {'create': self.create,
               'convert': self.convert,
               'change': self.change,
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
        return metadatasize


    def poolsize_compute(self):
        metadatasize = self.metadata_compute()
        pool_sz = floor(vg_size * 1024) - metadatasize
        snapshot_space = int(self.validated_params(
                'snapshot_reserve'))
        pool_sz -= (pool_sz * snapshot_space / 100)
        return pool_sz

    def validated_params(self, opt):
        value = self.module.params[opt]
        if value is None:
            msg = "Please provide %s option in the playbook!" % opt
            self.module.fail_json(msg=msg)
        return value

    def run_command(self, op, options):
        cmd = self.module.get_bin_path(op, True) + options
        return self.module.run_command(cmd)

    def create_thick_pool(self):
        compute_type = self.module.params['compute'] or ''
        compute_func = getattr(self, compute_type, None)
        try:
            size = compute_func()
        except:
            size = self.validated_params('size')
        pvname = self.module.params.get('pvname') or ''
        opts = ' -Wn -L %s -n %s %s %s' %(size, lvname, self.vgname, pvname)
        return opts

    def create_thin_pool(self):
        lvcreate = {}
        lvcreate['chunksize'] = self.get_thin_pool_chunk_sz()
        lvcreate['poolmetadatasize'] = self.module.params[
                'poolmetadatasize'] or ''
        lvcreate['thinpool'] = self.validated_params('poolname')
        lvcreate['size'] = self.module.params['size'] or ''
        cmd = self.parse_playbook_data(lvcreate)
        opts = ' -Wn %s' %cmd
        return opts

    def create_thin_lv(self):
        lvcreate = {}
        lvcreate['virtualsize'] = self.module.params[
                'virtualsize'] or self.poolsize_compute()
        lvcreate['name'] = self.validated_params('lvname')
        poolname = self.validated_params('poolname')
        cmd = self.parse_playbook_data(lvcreate)
        return ' --thin ' + cmd + ' ' + poolname

    def lv_presence_check(self, lvname):
        rc, out, err = self.run_command('lvdisplay', ' ' + lvname)
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

    def create(self):
        self.lvtype = self.validated_params('lvtype')
        lvname = self.validated_params('lvname')
        self.lv_presence_check(lvname)

        if self.lvtype in ['virtual']:
            poolname = self.validated_params('poolname')
        else:
            poolname = ''
        options = {'thick': self.create_thick_pool(),
                   'thinpool':  self.create_thin_pool(),
                   'thinlv': self.create_thin_lv()
                   }[self.lvtype]
                   # 'virtual': ' -V %sK -T /dev/%s/%s -n %s'
                   # % (pool_sz, self.vgname, poolname, lvname)
                   # }[self.lvtype]
        return options

    def get_thin_pool_chunk_sz(self):
        #As per performance enhancement specifications, to ensure best
        #performance, the thin pool chunksize should be 256KB for RAID6 and
        #JBOD and stripe unit size times the data disks count in case of RAID10
        #If disktype not specified will take user input for chunksize or
        #follow the default behaviour of lvconvert.
        disktype = self.module.params['disktype']
        chunksize = ''
        if disktype:
            stripe_unit_size = self.validated_params('stripesize')
            diskcount = validated_params('diskcount')
            chunksize = {'raid10': int(self.stripe_unit_size) * int(diskcount),
                         'raid6': 256,
                         'jbod': 256
                       }[self.disktype]
        if not chunksize:
            chunksize = self.module.params['chunksize']
        return chunksize

    def parse_playbook_data(self, dictionary, cmd):
        for key, value in dictionary.iteritems():
            if value:
                cmd += ' --%s %s ' % (key, value)
        return cmd

    def convert(self):
        lvconvert = {}
        lvconvert['type'] = self.module.params['lvtype']
        force = ''
        lvname = ''
        if self.module.params['force']:
            if self.module.params['force'].lower() == 'yes':
                force = ' force'
        if lvconvert.get('type'):
            if lvconvert['type'].lower() == 'cache-pool':
                poolmetadata = self.module.params['poolmetadata']
                if not '/' in poolmetadata:
                    poolmetadata = self.vg + '/' + poolmetadata
                lvcreate['poolmetada'] = poolmetadata

                lvconvert['cachemode'] = self.module.params[
                        'cachemode'] or 'writethrough'
            elif lvconvert['type'].lower() == 'cache':
                cachepool = self.validated_params(
                        'cachepool')
                if not '/' in cachepool:
                    cachepool == self.vg + '/' + cachepool
                lvconvert['cachepool'] = cachepool
            lv = self.validated_params('lvname')
            if not '/' in lv:
                lvname = self.vgname + '/' + self.validated_params('lv')
            else:
                lvname = lv
            self.lv_presence_check(lvname)

        lvconvert['thinpool'] = self.module.params[
                'thinpool'] or ''
        lvconvert['chunksize'] = self.get_thin_pool_chunk_sz()
        lvconvert['poolmetadataspare'] = self.module.params[
                'poolmetadataspare']
        lvconvert['options'] = self.module.params['options']
        cmd = self.parse_playbook_data(lvconvert, ' -ff --yes')
        return cmd + ' ' + lvname + force

    def change(self):
        poolname = self.validated_params('poolname')
        self.lv_presence_check(poolname)
        zero = self.module.params['zero'] or ''
        options = ' -Z %s %s/%s' % (zero, self.vgname, poolname)
        return options

    def remove(self):
        lvname = self.validated_params('lvname')
        self.lv_presence_check(lvname)
        opt = ' -ff --yes %s/%s' % (self.vgname, lvname)
        return opt


if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(choices=["create", "convert", "change", "remove"]),
            lvname=dict(),
            lv=dict(),
            cachemode=dict(),
            cachepool=dict(),
            lvtype=dict(),
            vgname=dict(),
            thinpool=dict(),
            poolmetadata=dict(),
            poolmetadataspare=dict(),
            poolname=dict(),
            zero=dict(),
            options=dict(),
            compute=dict(),
            disktype=dict(),
            diskcount=dict(),
            stripesize=dict(),
            snapshot_reserve=dict(),
            force=dict()
        ),
    )

    lvops = LvOps(module)
    cmd = lvops.lv_action()
    rc, out, err = lvops.run_command('lv' + lvops.action, cmd)
    lvops.get_output(rc, out, err)

