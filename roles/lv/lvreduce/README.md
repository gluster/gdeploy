lvreduce
=========
Reduce the size of a logical volume

Role Variables
--------------
    force
    extents [-]LogicalExtentsNumber[%{VG|LV|FREE|ORIGIN}]
    size [-]LogicalVolumeSize[bBsSkKmMgGtTpPeE]
    nofsck
    resizefs


Example Playbook to call the role
---------------------------------
---
- hosts: servers roles:
  roles:
  - ../lvreduce

Example of variable values that can be passed
---------------------------------------------
action: reduce
force: y
vgname: vg1
lvname: lvol1
nofsck: n
resizefs: n
size: -54M
pvname: /dev/vdb2
