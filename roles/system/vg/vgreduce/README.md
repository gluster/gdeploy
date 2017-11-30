vgreduce
=========
vgreduce role allows you to remove unused physical volumes from a volume group.

Requirements
------------
A volume group created on the PhysicalDevicePath.

Role Variables
--------------
vgname: Name of the volume group.
disk: Disk or partition on which the pv is created.

Example Playbook to call the role
---------------------------------
- hosts: servers
  roles:
     - ../vgreduce
Example of variable values that can be passed
---------------------------------------------
    action: reduce
    vgname: <vgname>
    disk: <disk>
