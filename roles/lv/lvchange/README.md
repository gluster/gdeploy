lvchange
=========

lvchange allows you to change the attributes of a logical volume including making them known to the kernel ready for use.

Role Variables
--------------

    errorwhenfull {y|n}
    permission {r|rw}
    zero {y|n}

Example Playbook to call the role
---------------------------------
---
- hosts: servers roles:
  roles:
  - ../lvcreate

Example of variable values that can be passed
---------------------------------------------
action: change
zero: n
vgname: vg1
lvname: lv1
errorwhenfull: n
permission: r
