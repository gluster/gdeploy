Creating a volume and setting a tuning profile on it
====================================================

This document will walk you through how you can create a Gluster volume and set a profile on it. Profiles are directories of files that contain settings to enhance performance of a volume. There are many profiles that come with Red Hat Gluster Storage and these are tailored for different workloads. One can also define or create a new profile. As profiles aid in performance tuning (improving system performance), they are also called as "tuning profiles".

Pre-defined profiles can be found here as subdirectories: /etc/tune-profiles.

For instance, /etc/tune-profiles/virtual-guest contains all the files and settings for the virtual-guest profile, which is a profile that sets performance options for virtual machines.

The following steps will illustrate how to create a volume and set a tuning profile on it.

**Step 1:**

Create the following configuration file::

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

	#The above section creates the volume. The below section will apply a profile to it.

	[tune-profile]
	rhgs-sequential-io 

	#This will set the profile 'rhgs-sequential-io'.

	
**Step 2:**

Invoke gdeploy and run this using::

	$gdeploy -c tune_profile.conf

where "tune_profile.conf" is the name of our configuration file created in Step 1.

**Step 3:**

Check whether this has been applied using::

	$tuned-adm list

This command, when run on any of the hosts / cluster nodes, will return you the list of available profiles along with the current active profile. In our case, the current active profile would be 'rhgs-sequential-io'.

