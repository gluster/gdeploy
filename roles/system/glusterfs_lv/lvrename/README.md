lvrename
=========
lvrename renames an existing logical volume or an existing historical logical volume

Requirements
------------
Exiting LV.

Role Variables
--------------
vgname
lvname
new_name

Example Playbook to call the role
---------------------------------
---
- hosts: servers roles:
  roles:
  - ../lvrename

  Example of variable values that can be passed
  ---------------------------------------------
  action: rename
  vgname: vg1
  lvname: lvol1
  new_name: lv1
