lvremove
=========
Remove a logical volume

Requirements
------------
Existing logical volume and Volume group.

Role Variables
--------------
force {y|n}

Example Playbook
----------------
---
- hosts: servers roles:
  roles:
  - ../lvremove

Example of variable values that can be passed
---------------------------------------------
action: remove
vgname: vg1
lvname: lvol1
