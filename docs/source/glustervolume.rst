Using gdeploy to create a 3x3 Gluster Volume
============================================

Here, we will see how we can create a 3-replica distributed Gluster volume using 3 nodes.

Pre-requisites: 

GlusterFS should be installed on all the three nodes and the service should be started using::

	$systemctl start glusterd.service


**Step 1:**

Create the following configuration file::

   [hosts]
   #Enter the ip addresses of all the three nodes here
   10.70.47.17
   10.70.46.173
   10.70.47.97

                                                                                  
   # Common backend setup for all three hosts.

   [backend-setup]
   devices=/dev/vdb
   vgs=vg2
   pools=pool1
   lvs=lv2
   mountpoints=/mnt/data1
   brick_dirs=/mnt/data1/1

   [peer]
   manage=probe

   [volume]
   action=create
   volname=sample_volname
   replica=yes
   replica_count=3 #Since we need three replicas
   force=yes

   # Enter client details here

   [clients]
   action=mount
   volname=sample_volname
   hosts=192.168.122.19
   fstype=glusterfs
   client_mount_points=/home/poo/client_mount_local


**Step 2:**

Save the file by giving it some name e.g. 'gluster3example.conf'. Invoke gdeploy and run the file using::

	$gdeploy -c gluster3example.conf

**Step 3:**

You can check whether a gluster volume is created by running the following command on all the three nodes::

	$gluster vol info

**Step 4:**

Write to the volume using your client machine (192.168.122.19 in our case) by traversing to the path you have mentioned under "client_mount_points" using the following command::

	$touch sample.txt

This command will create a file named as "sample.txt" under the directory "/home/poo/client_mount_local".

You can check whether the file has been replicated thrice by traversing to the path "/mnt/data1/1" on all three nodes and running the command::

	$ls

You will see three copies of your file on the nodes. 

You have successfully setup a 3x3 Gluster volume using gdeploy.
