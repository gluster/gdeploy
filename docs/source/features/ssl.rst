.. _rst_gdeployssl:

SSL
^^^

*New in gdeploy 2.0.1*

User can create volumes with SSL enabled, or enable ssl on exisiting volumes
using gdeploy (v2.0.1 onwards). This section explains how the configuration
files should be written for gdeploy to enable SSL. For documentatoin on SSL
please refer this `blog
<https://kshlm.in/post/network-encryption-in-glusterfs/>`_ and documentation
available in `Admin Guide.
<https://gluster.readthedocs.io/en/latest/Administrator%20Guide/SSL/>`_

1. Create a volume and enable SSL on it::

   [hosts]
   10.70.37.147
   10.70.37.47

   [backend-setup]
   devices=/dev/vdb
   vgs=vg1
   pools=pool1
   lvs=lv1
   mountpoints=/mnt/brick

   [volume]
   action=create
   volname=foo
   transport=tcp
   replica_count=2
   force=yes
   enable_ssl=yes
   ssl_clients=10.70.37.107,10.70.37.173
   brick_dirs=/data/1

   [clients]
   action=mount
   hosts=10.70.37.173,10.70.37.107
   volname=foo
   fstype=glusterfs
   client_mount_points=/mnt/data

In the above example, a volume named foo is created and SSL is enabled on
it. gdeploy creates self signed certficates.


2. Enable SSL on an existing volume::

     [hosts]
     10.70.37.147
     10.70.37.47

     # This is important. Clients have to be unmounted before setting up SSL
     [clients1]
     action=unmount
     hosts=10.70.37.173,10.70.37.107
     client_mount_points=/mnt/data

     [volume]
     action=enable-ssl
     volname=bar
     ssl_clients=10.70.37.107,10.70.37.173

     [clients2]
     action=mount
     hosts=10.70.37.173,10.70.37.107
     volname=bar
     fstype=glusterfs
     client_mount_points=/mnt/data

Note that in the volume section action is set to enable-ssl for an existing
volume. In case of existing the variable 'enable_ssl' shouldn't be used.
