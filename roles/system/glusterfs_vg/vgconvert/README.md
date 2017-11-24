vgconvert
=========
 vgconvert role converts VolumeGroupName metadata from one format to another provided that the metadata fits into the same space.

Requirements
------------
A volume group created on the PhysicalDevicePath.

Role Variables
--------------
vgname: Name of the volume group.
metadatatype:

Example Playbook to call the role
---------------------------------
- hosts: servers
  roles:
     - ../vgconvert

Example of variable values that can be passed
---------------------------------------------
    action: convert
    vgname: <vgname>
    metadatatype: 1
