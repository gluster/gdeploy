vgcreate
=========
vgcreate role creates a new volume group called VolumeGroupName using the block special device PhysicalDevicePath.

Requirements
------------
If  PhysicalDevicePath  was not previously configured for LVM with pvcreate, the device will be initialized with the same default values used with pvcreate.  

Role Variables
--------------
disk: disk or partition on which the pv is created.
zero (-Z)
Whether or not the first 4 sectors of the device should be wiped.
dataalignment(--dataalignment)
Align the start of the data to a multiple of this number.
maxlogicalvolumes(-l)
Sets the maximum number of logical volumes allowed in this volume group.
maxphysicalvolumes(-p)
Sets  the  maximum  number  of physical volumes that can belong to this volume group.

Example Playbook to call the role
---------------------------------
- hosts: servers
  roles:
     - ../vgcreate

Example of variable values that can be passed
---------------------------------------------
    action: create
    vgname: <vgname>
    disk: <disk>
    zero: y
    dataalignment: 1280
    maxlogicalvolumes: 2
    maxphysicalvolumes: 2
