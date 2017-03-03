.. _rst_gdeployclients:

Clients
^^^^^^^

*clients* module allows user to specify the client hosts and client_mount_points
to mount or unmount the gluster storage volume created.
The 'action' option is to be specified for the framework to determine the
action that has to be performed.
'action' variable can be any of *mount* and *unmount*.

Both *mount* and *unmount* option support the following variables:
1. hosts - The clients 'hosts' field is mandatory.
2. client_mount_points - Mountpoint directories. Where the logical volumes have
   to be mounted, if the mount points are not specified, default will be taken
   as /mnt/gluster for all the hosts.

*mount* option supports a few more variables:
3. fstype - The option fstype specifies how the gluster volume is to be mounted,
   default is glusterfs (FUSE mount). the volume can also be mounted as NFS.
   Each client can have different types of volume mount, which has to be
   specified with a comma seperated.
4. volname - This option specifies the volume name. Default name is glustervol.


For example::

Mount the specified hosts to the specified mount-point::

  [clients]
  action=mount
  hosts=10.0.0.10
  fstype=nfs
  nfs-version=3
  client_mount_points=/mnt/rhs
