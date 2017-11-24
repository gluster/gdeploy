lvextend
=========
Extend the size of a logical volume.
lvextend allows you to extend the size of a logical volume

Requirements
------------
Existing LV and a physical volume. This is only possible if the PV is a member
of volume group and there are enough free physical extents in it.

Role Variables
--------------
force
extents [+]LogicalExtentsNumber[%{VG|LV|PVS|FREE|ORIGIN}]
size [+]LogicalVolumeSize[bBsSkKmMgGtTpPeE]
stripesize StripeSize
nofsck
resizefs

Example Playbook to call the role
---------------------------------
---
- hosts: servers roles:
  roles:
  - ../lvextend

Example of variable values that can be passed
---------------------------------------------
action: extend
force: n
vgname: vg1
lvname: lvol1
nofsck: n
resizefs: n
size: +54
pvname: /dev/vdb2
