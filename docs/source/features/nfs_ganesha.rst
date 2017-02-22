.. _rst_nfsganesha:

Configuring NFS Ganesha
^^^^^^^^^^^^^^^^^^^^^^^

*New in gdeploy 2.0.1*

gdeploy supports the deployment and configuration of NFS Ganesha from version
2.0.1

NFS Ganesha module in gdeploy allows user to perform the following actions::

  1. create-cluster
  2. destroy-cluster
  3. add-node
  4. delete-node
  5. export-volume
  6. unexport-volume
  7. refresh-config

This document explains all the above actions with example configuration files.

create-cluster
==============

This action will create a fresh NFS-Ganesha setup on a given volume. For this
action nfs-ganesha section support the following variables::

  1. ha-name
  2. cluster-nodes
  3. vip
  4. volname

* ha-name: This is optional variable. By default ganesha-ha-360 will be used.
* cluster-nodes: This is a required argument, this variable expects comma
                 separated values of cluster node names, which should be used to
                 form the cluster.
* vip: This is a required argument, this variable expects comma separated list
       of ip addresses. These will be the virtual ip addresses.
* volname: This is a optional variable if the configuration contains [volume]
           section, else volname has to be mentioned and that volume should be
           present.

Example: Create a NFS-Ganesha cluster::

  [hosts]
  host-1.example.com
  host-2.example.com

  [backend-setup]
  devices=/dev/vdb
  vgs=vg1
  pools=pool1
  lvs=lv1
  mountpoints=/mnt/brick

  [firewalld]
  action=add
  ports=111/tcp,2049/tcp,54321/tcp,5900/tcp,5900-6923/tcp,5666/tcp,16514/tcp,662/tcp,662/udp
  services=glusterfs,nlm,nfs,rpc-bind,high-availability,mountd,rquota

  [volume]
  action=create
  volname=ganesha
  transport=tcp
  replica_count=2
  force=yes

  #Creating a high availability cluster and exporting the volume
  [nfs-ganesha]
  action=create-cluster
  ha-name=ganesha-ha-360
  cluster-nodes=host-1.example.com,host-2.example.com
  vip=10.70.44.121,10.70.44.122
  volname=ganesha


The above configuration file assumes, necessary packages are installed. Creates
a volume and enables NFS-Ganesha on it. If the configuration file is saved in
ganesha.conf, execute the configuration using the command:

* gdeploy -c ganesha.conf

Example on how to subscribe and install necessary Ganesha packages can be found
`here. <https://github.com/gluster-deploy/gdeploy/blob/master/examples/nfs_ganesha.conf>`_

destroy-cluster
===============

Action destroy-cluster cluster will disable NFS Ganesha. It allows one variable
'cluster-nodes'.

Example: Destroy NFS-Ganesha Cluster::

  [hosts]
  host-1.example.com
  host-2.example.com

  # To destroy the high availability cluster

  [nfs-ganesha]
  action=destroy-cluster
  cluster-nodes=host-1.example.com,host-2.example.com

add-node
========

Action add-node allows two variables::

  1. nodes
  2. vip

Both the variables are mandatory. 'nodes' takes a list of comma separated
hostnames that have to be added to the cluster and 'vip' takes a list of comma
separated ip addresses.

Example::

  [hosts]
  host-1.example.com
  host-2.example.com

  [nfs-ganesha]
  action=add-node
  nodes=host-3.example.com
  vip=10.0.0.33


delete-node
===========

Action delete-node deletes a node from NFS Ganesha cluster. delete-node takes
one variable 'nodes'.

Example::

  [hosts]
  host-1.example.com
  host-2.example.com

  [nfs-ganesha]
  action=delete-node
  nodes=host-3.example.com

export-volume
=============

Action export-volume exports a volume. export-volume action supports one
variable 'volname'.

Example::

  [hosts]
  host-1.example.com
  host-2.example.com

  [nfs-ganesha]
  action=export-volume
  volname=ganesha

unexport-volume
===============

Action unexport-volume unexports a volume. unexport-volume action supports one
variable 'volname'.

Example::

  [hosts]
  host-1.example.com
  host-2.example.com

  [nfs-ganesha]
  action=unexport-volume
  volname=ganesha

refresh-config
==============

Action refresh-config will add/delete or add a config block to the configuration
file and runs --refresh-config on the cluster.

Action refresh-config supports the following variables::

  1. add-config-lines
  2. del-config-lines
  3. update-config-lines
  4. block-name
  5. volname
  6. ha-conf-dir

Example 1 - Add a client block and run-refresh config::

  # config-block: is the variable containing lines (| separated) which will be
  # added to the client block.
  #
  # The client block will look something like:
  #   client {
  # clients = 10.0.0.1;
  # allow_root_access = true;
  # access_type = "RO";
  # Protocols = "3";
  # anonymous_uid = 1440;
  # anonymous_gid = 72;
  # }
  #

  [hosts]
  dhcp37-102.lab.eng.blr.redhat.com
  dhcp37-103.lab.eng.blr.redhat.com

  [nfs-ganesha]
  action=refresh-config
  # Default block name is `client'
  block-name=client
  config-block=clients = 10.0.0.1;|allow_root_access = true;|access_type = "RO";|Protocols = "2", "3";|anonymous_uid = 1440;|anonymous_gid = 72;
  volname=ganesha


Example 2 - Add a line and run refresh-config::

  [hosts]
  dhcp37-102.lab.eng.blr.redhat.com
  dhcp37-103.lab.eng.blr.redhat.com

  [nfs-ganesha]
  action=refresh-config
  add-config-lines=clients = 10.0.0.1;|anonymous_gid = 72;
  volname=ganesha

Example 3 - Delete a line and run refresh-config::

  [hosts]
  dhcp37-102.lab.eng.blr.redhat.com
  dhcp37-103.lab.eng.blr.redhat.com

  [nfs-ganesha]
  action=refresh-config
  del-config-lines=client
  volname=ganesha

Example 4 - Update a line and run refresh-config::

  [hosts]
  dhcp37-102.lab.eng.blr.redhat.com
  dhcp37-103.lab.eng.blr.redhat.com

  [nfs-ganesha]
  action=refresh-config
  update-config-lines=access_type = "RW";|anonymous_gid = 72;
  volname=ganesha

Example 5 - Run refresh-config on a volume::

  [hosts]
  dhcp37-102.lab.eng.blr.redhat.com
  dhcp37-103.lab.eng.blr.redhat.com

  [nfs-ganesha]
  action=refresh-config
  volname=ganesha


