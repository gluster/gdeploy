NFS Ganesha setup end-to-end
============================

Here we'll see how we can setup NFS Ganesha using gdeploy. We'll be writing a configuration file for the end-to-end setup, right from creating a volume, subscribing to channels and installing the right packages. This configuration file will also create a high availability cluster and export the volume.

**Step 1:**

Create an empty .conf file with the following::

	[hosts]
	dhcp37-102.lab.eng.blr.redhat.com
	dhcp37-103.lab.eng.blr.redhat.com

	[backend-setup]
	devices=/dev/vdb
	vgs=vg1
	pools=pool1
	lvs=lv1
	mountpoints=/mnt/brick

	# Subscribe to necessary channels
	[RH-subscription1]
	action=register
	username=<username>
	password=<password>
	pool=<pool>

	[RH-subscription2]
	action=disable-repos
	repos=

	[RH-subscription3]
	action=enable-repos
	repos=rhel-7-server-rpms,rh-gluster-3-for-rhel-7-server-rpms,rh-gluster-3-nfs-for-rhel-7-server-rpms,rhel-ha-for-rhel-7-server-rpms

	#Installing nfs-ganesha
	[yum]
	action=install
	repolist=
	gpgcheck=no
	update=no
	packages=glusterfs-ganesha

	#Enabling the firewall service and configuring necessary ports
	[firewalld]
	action=add
	ports=111/tcp,2049/tcp,54321/tcp,5900/tcp,5900-6923/tcp,5666/tcp,16514/tcp,662/tcp,662/udp
	services=glusterfs,nlm,nfs,rpc-bind,high-availability,mountd,rquota

	#This will create a volume. Skip this section if your volume already exists
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
	cluster-nodes=dhcp37-102.lab.eng.blr.redhat.com,dhcp37-103.lab.eng.blr.redhat.com
	vip=10.70.44.121,10.70.44.122
	volname=ganesha

**Step 2:**

Run this file using::

	$gdeploy -c nfs_ganesha1.conf

where nfs_ganesha1.conf is the name of our configuration file saved in Step 1.

**Step 3:**

To see if your volume has been exported, you may run this command on any or all of the nodes::

	$showmount -e localhost

