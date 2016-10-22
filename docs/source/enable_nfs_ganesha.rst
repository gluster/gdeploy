Enabling NFS Ganesha on a Gluster volume
=======================================

**Step 1:**

Create a '.conf' file with the following contents::
	
	[hosts]
	dhcp37-102.lab.eng.blr.redhat.com
	dhcp37-103.lab.eng.blr.redhat.com

	[nfs-ganesha]
	action=create-cluster
	ha-name=ganesha-ha-360
	cluster-nodes=dhcp37-102.lab.eng.blr.redhat.com,dhcp37-103.lab.eng.blr.redhat.com
	vip=10.70.44.121,10.70.44.122
	volname=ganesha

**Step 2:**

Invoke gdeploy to run the file using the command::

	$gdeploy -c nfs_ganesha1.conf

'nfs_ganesha1.conf' is the name of our configuration file created in Step 1.
