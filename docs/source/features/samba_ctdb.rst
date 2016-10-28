.. _rst_sambactdb:

Setting up Samba and CTDB
^^^^^^^^^^^^^^^^^^^^^^^^^

*New in gdeploy 2.0.1*

gdeploy supports the deployment of `Samba`_ and `CTDB`_ from release 2.0.1.

Samba
=====

gdeploy provides provision to setup Samba in two scenarios.

1. `Enable Samba on an existing volume`_
2. `Enable Samba while creating a volume`_

Below documentation explains both the methods

Enable Samba on an existing volume
----------------------------------

     If a GlusterFS volume is already present, then user has to mention the
     action as 'smb-setup' in the volume section. It is necessary to mention all
     the hosts that are in the cluster, as gdeploy updates the glusterd
     configuration files on each of the hosts.

     For example::

       [hosts]
       10.70.37.192
       10.70.37.88

       [volume]
       action=smb-setup
       volname=samba1
       force=yes
       smb_username=smbuser
       smb_mountpoint=/mnt/smb

     In the above example ensure that host are not part of CTDB cluster.


Enable Samba while creating a volume
------------------------------------

      If Samba has be set up while creating a volume, a variable smb has to be
      set to yes.

      For example::

        [hosts]
        10.70.37.192
        10.70.37.88

        [backend-setup]
        devices=/dev/vdb
        vgs=vg1
        pools=pool1
        lvs=lv1
        mountpoints=/mnt/brick

        [volume]
        action=create
        volname=samba1
        smb=yes
        force=yes
        smb_username=smbuser
        smb_mountpoint=/mnt/smb

In both the cases note that, smb_username and smb_mountpoint are necessary if
samba has to be setup with proper acls set.


CTDB
====

gdeploy configuration files for CTDB setup can be written to setup CTDB while
creating volumes, or to setup CTDB on existing volumes.

gdeploy allows users to setup CTDB using different ip addresses than mentioned
in 'hosts' section. For example if a user has internal ip addresses on which to
he decides to setup CTDB cluster, those ip addresses have to be set in
ctdb_nodes variable.

Example 1: Setup CTDB on an existing volume named foo::

  [hosts]
  10.70.37.192
  10.70.37.88

  [ctdb]
  action=setup
  public_address=10.70.37.6/24 eth0,10.70.37.8/24 eth0
  volname=foo

Example 2: Create a volume and setup CTDB::

  [hosts]
  10.70.37.192
  10.70.37.88

  [volume]
  action=create
  volname=ctdb
  transport=tcp
  replica_count=2
  force=yes

  [ctdb]
  action=setup
  public_address=10.70.37.6/24 eth0,10.70.37.8/24 eth0

Example 3: Setup CTDB, use separate ip addresses for CTDB cluster::

  [hosts]
  10.70.37.192
  10.70.37.88

  [ctdb]
  action=setup
  public_address=10.70.37.6/24 eth0,10.70.37.8/24 eth0
  ctdb_nodes=192.168.1.1,192.168.2.5
  volname=samba1
