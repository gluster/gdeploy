Unexporting a volume and destroying an NFS-Ganesha HA Cluster
=============================================================

Here, we'll see how we can unexport a volume and destroy a high availability cluster.

**Step 1:**

Create the following configuration file::

	[hosts]
	dhcp37-102.lab.eng.blr.redhat.com
	dhcp37-103.lab.eng.blr.redhat.com

	# To un-export the volume:

	[nfs-ganesha1]
	action=unexport-volume
	volname=ganesha

	# To destroy the high availability cluster

	[nfs-ganesha2]
	action=destroy-cluster
	cluster-nodes=dhcp37-102.lab.eng.blr.redhat.com,dhcp37-103.lab.eng.blr.redhat.com

'ganesha' is the name of our volume.

**Step 2:**

Run this file using::

	$gdeploy -c ganesha_destroy.conf

Here, "ganesha_destroy.con" is the name of our configuration file created in Step 1.

**Step 3:**

Now, when you run this command on any or all of the nodes in the cluster, you will not see any mounts for nfs-ganesha::

	$showmount -e localhost

You have successfully unexported the volume and destroyed the HA cluster.
