# Gluster Deploy - Tool to install and configure GlusterFS

Introduction
============

Gluster Deploy (gdeploy), deploys configurations. A configuration can be:

* Backend setup configuration.
* Gluster cluster setup (Volume configuration).
* Client (mount) configuration.
* Feature configurations like:
  1. NFS-Ganesha configuration
  2. Samba configuration
  3. Snapshot configuration.
  4. Geo-replication configuration.
  5. Quota configuration

In addition to above configurations any volume set operation can be done from
the remote host. The CLI will be explained later.

The configurations can be put together or can be run individually. For example
creating backend, setting up a GlusterFS volume, and configuring NFS-Ganesha can
be one configuration or can be split up into three individual configurations.


Configuration files
===================

The configuration file is made up of sections. Currently supported sections
include:

* [hosts]
* [devices]
* [disktype]
* [diskcount]
* [stripesize]
* [vgs]
* [pools]
* [lvs]
* [mountpoints]
* {host-specific-data-for-above}
* [clients]
* [volume]
* [snapshot]


hosts
-------

This section will contain ip addresses or hostnames. Each
hostname or ip address should be listed in a separate line.
For operations like back-end setup, peer probe, volume create etc.,
this is a mandatory section.

devices
---------

Generic section [devices] is applicable to all the hosts listed in the [hosts]
section. However, if sections of hosts [hostname] or [ip-address] is present,
then the data in generic sections like [devices] are ignored. Host specific
data take precedence.

This is an optional section. If configuring `Backend setup configuration', the
devices should be either listed in this section or in the host specific
section.

disktype
----------

Section [disktype] specifies which disk configuration is used while
setting up the backend. Supports RAID 10, RAID 6 and JBOD configurations.
If this field is left empty, it will be by default taken as JBOD.
This is common for all the hosts.

This is an optional section with JBOD as default.

diskcount
-----------

Section [diskcount] specifies the number of data disks in the setup. This is a
mandatory field if the disk configuration specified is either RAID 10 or
RAID 6 and will be ignored if architecture is JBOD. This is host specific
data.

stripesize
------------

Section [stripesize] specifies the stripe_unit size in KB. This is a mandatory
field if disk configuration is RAID 6. If this is not specified in case of
RAID 10 configurations, it will take the default value 256K. This field is
not necessary for JBOD configuration of disks. Do not add any suffixes like
K, KB, M, etc. This is host specific data. Can be put into hosts section.


vgs
-----

vg names for the above devices, The number of vgs in the [vgs] should match the
devices.

If the vgnames are missing, volume groups will be named as RHS_vg{1, 2, 3, ...}.
as default.

pools
-------

pool names for the above volume groups.
The number of pools listed in the [pools] section should match the number of
vgs.

If the pool names are missing, pools will be named as RHS_pool{1, 2, 3, ...}.


lvs
-----

lv names for the above volume groups.
The number of logical volumes listed in the [lvs] section should match the
number of vgs.

If lv names are missing, logical volumes are named as RHS_lv{1, 2, 3, ...}.

mountpoints
-------------

Brick mountpoints for the logical volumes.
The number of mountpoints should match the number of logical volumes listed
above.

**IMP**: If only gluster deployment is to be done and not back-end setup, just
give this data about the hosts specified in the [hosts] section along
with the client data.

brick_dirs
------------

brick_dirs is the directory which is to be used as brick while creating the
volume. A mountpoint cannot be used as a brick directory, so brick_dirs
specifies the directory to be made inside the LV mount point that will be
used as a brick.

This field can be left empty in which case a directory will be created
inside the mountpoint with a default name. If backend setup is not being done
this field will be ignored. An option or section force can be used, in case
mountpoints should be used as the brick directories, in which case also this
field can be omitted.

{host-specific-data}
--------------------

For the hosts (ip/hostname) listed under `hosts` section, each host can have its
own specific data. The following are the variables that are supported for hosts.

Host specific data can be:
  * devices - List of devices to use
  * vgs - Custom VG names
  * pools - Custom POOL names
  * lvs - Custom LV names
  * mountpoints - Mount points for the logical names

peer
------

The section peer specifies the configurations for the Trusted Storage
Pool management(TSP)

This section helps in making all the hosts specified in the section `hosts`
to either probe each other making the TSP or detach all of them from TSP

The only option in this section is the option names `manage` which can have
it's values to be  either probe or detach

Conf data:
  * manage [Possible options are `probe` or `detach`]

clients
---------

Specifies the client hosts and client_mount_points to mount the gluster
volume created.

`action` option is to be specified for the framework to understand
what action is to be done. The options are `mount` and `unmount`
Client hosts field is mandatory. If mount points
are not specified, default will be taken as /mnt/gluster
for all the hosts

The option fstype specifies how gluster volume is to be mounted.
Default is glusterfs(FUSE mount). The volume can also be mounted as NFS.
Each client can have different types of volume mount. Just specify it comma
separated.

Fields include:
  * action=mount
  * hosts=10.70.46.13
  * fstype=glusterfs
  * client_mount_points=/mnt/gluster

volume
--------

The section volume specifies the configuration options for the volume.

`action` option specifies what action id to be performed in the volume.
The choices can be [create, delete, add-brick, remove-brick].
If delete is provided all the options other than `volname` will be ignored.
If add-brick or remove-brick is chosen, extra option bricks with a
comma separated list of brick names(in the format <hostname>:<brick path>
should be provided. In case of remove-brick, state option should also
be provided specifying the state of the volume after brick removal.

`volname` option specifies the volume name. Default is glustervol
 If the user wishes to do just a volume operation, she can omit the
 `hosts` section if the volname is provided in the format
 <hostname>:<volname>, where hostname is the hostname or IP of one of
 the nodes in the cluster
 IMP: Only single volume creation/deletion/configuration is supported
 as of now.

`transport` option specifies the transport type. Default is tcp. Options are
tcp or rdma or tcp,rdma

`replica` option will specify if the volume should be of type replica or not.
options are yes and no. Default is no.
If `replica` is given as yes, `replica_count` should be given.
Option `arbiter_count` is optional.

`disperse` option will specify if the volume should be of type disperse.
options are yes and no. Default is no.
`disperse_count` is optional even if the `disperse` is yes. if not specified,
the number of bricks specified in the command line is taken as the
disperse_count value.
If `redundancy_count` is not specified, and if `disperse` is yes,  it's
default value is computed so that it generates an optimal configuration.

Fields allowed in this section:
  * action=create
  * volname=glustervol
  * transport=tcp,rdma
  * replica=yes
  * replica_count=2
  * arbiter_count=2
  * disperse=yes
  * disperse_count=0
  * redundancy_count=2
  * force - Pass force option to volume create

snapshot
----------

`snapshot` section can be used if the user wants to create or delete
a snapshot.
The option `action` is to be used to specify which snapshot action is to be
executed. The choices supported as of now are create, delete, clone
and restore.
The name of the snapshot can be specified as the value to the snapname option.
If the action is create the name of the volume is to specified as the value
to the option `volname`.(If not specified under the volume section).

Fields in this section:
  * action=create
  * snapname=glustersnap


Of the above mentioned configurations, the tool itself does not mandate most of
the values.

# Brick configuration:

* [hosts]
* [devices]
* [disktype]
* [diskcount]
* [stripesize]

# Peer configuration

* [hosts]

# Volume configuration

* [hosts]
* [volume]
