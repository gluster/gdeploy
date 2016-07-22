Set a 5GB limit on a directory using quota
==========================================

Here, we will see how to set a 5GB limit on a directory within our volume using quota.

**Step 1:**

Create the following '.conf' file::

	#Enabling quota for this volume
	[quota]
	action=enable
	volname=10.70.41.236:1x2_vol

	# This will set up a quota limit for the specified path on the volume
	[quota]
	action=limit-usage
	volname=10.70.41.236:1x2_vol
	path=/main_dir
	size=5GB

**Step 2:**

Run the file using::

	$gdeploy -c 5gbquota.conf

Here, '5gbquota.conf' is the name of our configuration file created in Step 1.

**Step 3:**

You can check whether quota is enabled on your desired volume by checking volume information::

	$gluster vol info

This command needs to be run on the any or all of the machines on which the volume resides.

**Step 4:**

To check whether the size limit of 5GB has been set, we run the command::

	$gluster vol quota 1x2_vol list

This command gives us a detailed description of quota settings applied on our volume.





