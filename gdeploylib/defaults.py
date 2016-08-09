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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

# ALL features

feature_list = ['snapshot', 'quota', 'yum', 'geo_replication', 'ctdb',
'firewalld', 'nfs_ganesha', 'service', 'rh_subscription', 'shell',
'update_file', 'script', 'volume', 'peer', 'clients', 'pv', 'vg', 'lv',
'openshift_ctl']
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
PVRESIZE_YML = 'pvresize.yml'
LVCONVERT_YML = 'lvconvert.yml'
LVCREATE_YML = 'lvcreate.yml'
THINLVCREATE_YML = 'thin_lvcreate.yml'
LVCHANGE_YML = 'lvchange.yml'
VGEXTEND_YML = 'vgextend.yml'
GLUSTER_LV_YML = 'auto_lvcreate_for_gluster.yml'
VGCREATE_YML = 'vgcreate.yml'

SETUP_CACHE_YML = "cache_setup.yml"

TUNE_YML = 'tune-profile.yml'


BRESET_YML = 'backend-reset.yml'


PROBE_YML = 'gluster-peer-probe.yml'
DETACH_YML = 'gluster-peer-detach.yml'

SMBSRV_YML = 'mount-in-samba-server.yml'
SMBREPLACE_YML = 'replace_smb_conf_volname.yml'
SMB_FOR_CTDB = 'samba_for_ctdb.yml'

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

MNTCREATE_YML = 'create-mount-points.yml'
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
QUOTA_OPS = 'gluster-quota-ops.yml'
QUOTA_REMOVE = 'gluster-quota-remove.yml'
QUOTA_DSL = 'gluster-quota-dsl.yml'


# SUBSCRIPTION MANAGER

SUBS_MGMT = 'subscription_manager.yml'
DISABLE_REPO = 'disable-repos.yml'
ENABLE_REPO = 'enable-repos.yml'
UNREGISTER = 'redhat_unregister.yml'


# UPDATE FILE

ADD_TO_FILE = 'add-remote-file.yml'
EDIT_FILE = 'edit-remote-file.yml'
MOVE_FILE = 'move-file-from-local-to-remote.yml'


# FIREWALLD

PORT_OP = 'firewalld-ports-op.yml'
SERVICE_OP = 'firewalld-service-op.yml'


# YUM

YUM_OP = 'yum-operation.yml'

# MISC

SERVICE_MGMT = 'service_management.yml'
CHKCONFIG = 'chkconfig_service.yml'
SHELL_YML = 'shell_cmd.yml'

# CTDB

CTDB_SETUP = 'setup_ctdb.yml'

# GEO-REP

GEOREP_CREATE = 'georep-session-create.yml'
GEOREP_START = 'georep-session-start.yml'
GEOREP_STOP = 'georep-session-stop.yml'
GEOREP_DELETE = 'georep-session-delete.yml'
GEOREP_PAUSE = 'georep-session-pause.yml'
GEOREP_RESUME = 'georep-session-resume.yml'
GEOREP_CONFIG = 'georep-session-config.yml'
GEOREP_SS = 'georep-secure-session.yml'
SET_PERM_KEYS = 'georep-set-pemkeys.yml'
GEOREP_FAILBACK = 'georep-fail-back.yml'
PUBKEY_SHARE = 'georep_common_public_key.yml'


# NFS-GANESHA

GANESHA_BOOTSTRAP = 'bootstrap-nfs-ganesha.yml'
GANESHA_PUBKEY = 'generate-public-key.yml'
COPY_SSH = 'copy-ssh-key.yml'
SET_AUTH_PASS = 'set-pcs-auth-passwd.yml'
PCS_AUTH = 'pcs-authentication.yml'
SHARED_MOUNT = 'gluster-shared-volume-mount.yml'
GANESHA_CONF_CREATE = 'ganesha-conf-create.yml'
ENABLE_GANESHA = 'enable-nfs-ganesha.yml'
GANESHA_VOL_CONFS = 'ganesha-volume-configs.yml'
GANESHA_VOL_EXPORT = 'gluster-volume-export-ganesha.yml'
GANESHA_DISABLE = 'disable-nfs-ganesha.yml'
GANESHA_ADD_NODE = 'ganesha-cluster-add.yml'
GANESHA_DELETE_NODE = 'ganesha-cluster-delete.yml'
DEFINE_SERVICE_PORTS = 'define_service_ports.yml'

RUN_SCRIPT = 'run-script.yml'


# Kubectl

OC_CREATE = 'oc-create.yml'
OC_DELETE = 'oc-delete.yml'
