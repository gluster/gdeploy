examples
==============

Implementing quota to set size limit on a Gluster volume
========================================================

Here, we will see how we can create a 1x2 replica volume and then set a usage limit on it.  This means we would need 2 bricks and each file will have 2 replicas, one on each brick. 

As a recommended practice, our bricks reside on separate machines.

Pre-requisites: 

GlusterFS should be installed on both the nodes and the service should be started using::

	$systemctl start glusterd.service


**Step 1:**

Create the following configuration file::


	# This does backend setup first and then creates the volume using the
	# setup bricks.


	[hosts]
	10.70.41.236
	10.70.42.253

	# Common backend setup for 2 of the hosts.
	[backend-setup]
	devices=vda
	mountpoints=/mnt/data
	brick_dirs=/mnt/data/1

	# If backend-setup is different for each host
	# [backend-setup:192.168.122.109]
	# devices=sdb
	# brick_dirs=/gluster/brick/brick1
	#
	# [backend-setup:192.168.122.227]
	# devices=sda,sdb,sdc
	# brick_dirs=/gluster/brick/brick{1,2,3}
	#
	[peer]
	manage=probe

	[volume]
	action=create
	volname=1x2_vol
	replica=yes
	replica_count=2
	force=yes

	[clients]
	action=mount
	volname=1x2_vol
	hosts=10.70.41.236
	fstype=glusterfs
	client_mount_points=/glusterfs

	# This will set up a quota limit for the specified volume
	[quota]
	action=limit-usage
	volname=10.70.41.236:1x2_vol
	path=/mnt/data1/1
	size=10MB


**Step 2:**

Save the file by giving it some name e.g. '1x2volume.conf'. Invoke gdeploy and run the file using::

	$gdeploy -c 1x2volume.conf

**Step 3:**

You can check whether a gluster volume is created by running the following command on all the three nodes::

	$gluster vol info

**Step 4:**

Write to the volume using your client machine (10.70.41.236 in our case) by traversing to the path you have mentioned under "client_mount_points" using the following command::

	$touch sample.txt

This command will create a file named as "sample.txt" under the directory "/glusterfs".

You can check whether the file has been replicated twice by traversing to the path "/mnt/data1/1" on both the nodes and running the command::

	$ls

You will see two copies of your file in total, on the bricks. 

You have successfully setup a 1x2 Gluster volume using gdeploy and set a size limit on it.



