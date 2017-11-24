vgextend
=========
 vgextend role allows you to add one or more initialized physical volumes to an existing volume group to extend it in size.

Requirements
------------
A volume group created on the PhysicalDevicePath.

Role Variables
--------------
disk: disk or partition on which the pv is created.
zero (-Z)
Whether or not the first 4 sectors of the device should be wiped.
dataalignment(--dataalignment)
Align the start of the data to a multiple of this number.
metadatasize (--metadatasize)
Size of metadata
metadataignore (--metadataignore)
Enable or disable to ignore metadata

Example Playbook to call the role
---------------------------------
- hosts: servers
  roles:
     - ../vgextend
Example of variable values that can be passed
---------------------------------------------
    action: extend
    vgname: <vgname>
    disk: <disk>
    zero: y
    dataalignment: 1280
    metadatasize: 2
    metadataignore: y
