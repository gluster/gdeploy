vgremove
=========
vgremove allows you to remove one or more volume groups.

Requirements
------------
A volume group created on the PhysicalDevicePath.

Role Variables
--------------
force:  Force the removal of any volume group without confirmation.
vgname: name of the volume group to be removed.

Example Playbook to call the role
---------------------------------
- hosts: servers
  roles:
     - ../vgremove
Example of variable values that can be passed
---------------------------------------------
    action: remove
    vgname: <vgname>
    force: y
