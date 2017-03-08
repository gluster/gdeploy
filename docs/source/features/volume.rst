.. _rst_glusterfsvolume:

Creating GlusterFS Volumes
^^^^^^^^^^^^^^^^^^^^^^^^^^

The *volume* module allows users to create volume using a specified list of
hosts and bricks. Volume section supports the following variables:

1. volname - Name of the volume, if no name is provided gdeploy generates a
   volume name.
2. action - Action supports the following values *create*, *delete*,
   *add-brick*, *remove-brick*, *rebalance*, and *set*.
3. brick_dirs - This variable specifies the brick directories to use. The
   brick_dirs variable can take values in ip:brick_dir format or just brick_dir
   format. For example:

   brick_dirs=10.0.0.1:/mnt/data1/1,10.0.0.2:/mnt/data2/2

   Or

   brick_dirs=/mnt/data1/1,/mnt/data2/2
4. transport - The transport type. Possible values are tcp,tcp,rdma,rdma
5. replica_count - The replication count for replica volumes.
6. force - If set to yes, force is used while creating volumes.
7. disperse - Identifies if the volume should be disperse. Possible options are
   [yes, no].
8. disperse_count - Optional argument. If none given, the number of bricks
   specified in the commandline is taken as the disperse_count value.
9. redundancy_count - If redundancy_count is not specified, and if *disperse* is
   yes, it's default value is computed so that it generates an optimal
   configuration.

Example 1::

  [volume]
  action=create
  volname=foo
  transport=tcp
  replica_count=2
  force=yes

Example 2::

  [backend-setup]
  devices=sdb,sdc
  vgs=vg1,vg2
  pools=pool1,pool2
  lvs=lv1,lv2
  brick_dirs=/gluster/brick/brick{1,2}

  # If backend-setup is different for each host
  # [backend-setup:10.70.46.13]
  # devices=sdb
  # brick_dirs=/gluster/brick/brick1
  #
  # [backend-setup:10.70.46.17]
  # devices=sda,sdb,sdc
  # brick_dirs=/gluster/brick/brick{1,2,3}
  #

  [volume]
  action=create
  volname=sample_volname
  replica=yes
  replica_count=2
  force=yes
