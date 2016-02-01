#!/usr/bin/python
# -*- coding: utf-8 -*- #
#
# Copyright 2016 Nandaja Varma <nvarma@redhat.com>
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

# All the defaults values used in gdeploy


VOLUME_CREATE_DEFAULTS =  {
                            'transport': 'tcp',
                            'replica': 'no',
                            'disperse': 'no',
                            'replica_count': 0,
                            'arbiter_count': 0,
                            'disperse_count': 0,
                            'redundancy_count': 0
                          }


REPLICA_DEFAULTS        = {
                            'replica': 'no',
                            'replica_count': 0
                          }

BRESET_DEFAULTS         = {
                            'pvs': None,
                            'vgs': None,
                            'lvs': None,
                            'mountpoints': None,
                            'unmount': "no"
                          }

BSETUP_DEFAULTS         = {
                            'vgs': 'GLUSTER_vg',
                            'pools': 'GLUSTER_pool',
                            'lvs': 'GLUSTER_lv',
                            'mountpoints': '/gluster/brick'
                          }

# The Playbook files
SELINUX_YML = 'set-selinux-labels.yml'
MOUNT_YML = 'mount.yml'
FSCREATE_YML = 'fscreate.yml'
PVCREATE_YML = 'pvcreate.yml'
LVCONVERT_YML = 'lvconvert.yml'
LVCREATE_YML = 'lvcreate.yml'
VGEXTEND_YML = 'vgextend.yml'
GLUSTER_LV_YML = 'auto_lvcreate_for_gluster.yml'
VGCREATE_YML = 'vgcreate.yml'

TUNE_YML = 'tune-profile.yml'


BRESET_YML = 'backend-reset.yml'


GLUSTERD_YML = 'glusterd-start.yml'
PROBE_YML = 'gluster-peer-probe.yml'
DETACH_YML = 'gluster-peer-detach.yml'

SMBSRV_YML = 'mount-in-samba-server.yml'
SMBREPLACE_YML = 'replace_smb_conf_volname.yml'
VOLUMESET_YML = 'gluster-volume-set.yml'
REBALANCE_YML = 'gluster-volume-rebalance.yml'
VOLUMESTART_YML = 'gluster-volume-start.yml'
REMOVEBRK_YML = 'gluster-remove-brick.yml'
ADDBRICK_YML = 'gluster-add-brick.yml'
VOLDEL_YML = 'gluster-volume-delete.yml'
VOLSTOP_YML = 'gluster-volume-stop.yml'
VOLSTART_YML = 'gluster-volume-start.yml'
VOLCREATE_YML = 'gluster-volume-create.yml'
CREATEDIR_YML = 'create-brick-dirs.yml'

CIFSMNT_YML = 'gluster-client-cifs-mount.yml'
NFSMNT_YML = 'gluster-client-nfs-mount.yml'
FUSEMNT_YML = 'gluster-client-fuse-mount.yml'
VOLUMOUNT_YML = 'client_volume_umount.yml'



# FEATURE YMLs

#SNAPSHOT
SNAPSHOT_CREATE = 'gluster-snapshot-create.yml'
SNAPSHOT_DELETE = 'gluster-snapshot-delete.yml'
SNAPSHOT_CLONE = 'gluster-snapshot-clone.yml'
SNAPSHOT_RESTORE = 'gluster-snapshot-restore.yml'
SNAPSHOT_ACTIVATE = 'gluster-snapshot-activate.yml'
SNAPSHOT_DEACTIVATE = 'gluster-snapshot-deactivate.yml'
SNAPSHOT_CONFIG = 'gluster-snapshot-config.yml'

#QUOTA
QUOTA_ENABLE = 'gluster-quota-enable.yml'
QUOTA_DISABLE = 'gluster-quota-disable.yml'
QUOTA_LIMIT_USAGE = 'gluster-quota-limit-size.yml'
QUOTA_LIMIT_OBJECTS = 'gluster-quota-limit-object.yml'
QUOTA_OPS = 'gluster-quota-disable.yml'


