lvresize
=========
lvresize allows you to resize a logical volume

Role Variables
--------------
    force
    nofsck
    resizefs
    extents [+|-]LogicalExtentsNumber[%{VG|LV|PVS|FREE|ORIGIN}]
    size [+|-]LogicalVolumeSize[bBsSkKmMgGtTpPeE]
    stripes Stripes
    poolmetadatasize [+]MetadataVolumeSize[bBsSkKmMgG]
    stripesize StripeSize


Example Playbook to call the role
---------------------------------
---
- hosts: servers roles:
  roles:
  - ../lvrename

Example of variable values that can be passed
---------------------------------------------
action: resize
lvname: lv1
vgname: vg1
force: y
extents: VG
size: +1M
stripe: n
