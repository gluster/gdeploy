# Roles

Roles to deploy GlusterFS and implementing other use cases.

## Roles for gdeploy

### System

  - glusterfs_pv  - Create pv on all disks
  - glusterfs_vg  - Create a volume group
  - glusterfs_lv  - Create a logical volume
  - mount         - mount a logical volume, or a GlusterFS volume
  - umount        - unmount a logical volume, or a GlusterFS volume

### glusterfs
  - peer_probe           --- Peer probe a node; add a node to cluster    
  - peer_detach          --- Detach a node from the cluster   
  - volume_create        --- Create a GlusterFS volume   
  - volume_delete        --- Delete a GlusterFS volume   

### georeplication
  - georep_create        --- Create a geo-replication session (Secure and root)   
  - georep_delete        --- Delete a geo-replication session   
  - georep_pause         --- Pause a geo-replication session   
  - georep_resume        --- Resume a geo-replication session   
  - georep_start         --- Start a geo-replication session   
  - georep_stop          --- Stop a geo-replication session   

### nfs_ganesha
  - nfs_ganesha_create   
  - nfs_ganesha_destroy   
  - nfs_ganesha_add_node   
  - nfs_ganesha_del_node   
  - nfs_ganesha_export_vol   
  - nfs_ganesha_unexport_vol   
  - nfs_ganesha_refresh_conf
  
### ctdb
  - ctdb_setup   
  - ctdb_enable   
  - ctdb_disable   
  - ctdb_stop   
  - ctdb_start   

### Quota
  - quota_enable   
  - quota_disable   
  - quota_remove   
  - quota_remove_objects   
  - quota_default_soft_limits   
  - quota_limit_usage   
  - quota_limit_objects  
  - quota_alert_time  
  - quota_soft_timeout  
  - quota_hard_timeout
  
### glusterfs_clients
  - glusterfs_client_mount  
  - glusterfs_client_umount  

### glusterfs_snapshot
  - glusterfs_snapshot_create  
  - glusterfs_snapshot_delete  
  - glusterfs_snapshot_activate  
  - glusterfs_snapshot_deactivate  
  - glusterfs_snapshot_clone  
  - glusterfs_snapshot_restore  
  - glusterfs_snapshot_config  
