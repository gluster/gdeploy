lvcreate
=========
Create a logical volume in an existing volume group

Requirements
------------
lvcreate creates a new logical volume in a volume group by allocating logical
extents from the free physical extent pool of that volume group.

Role Variables
--------------
cachemode {passthrough|writeback|writethrough}
chunksize ChunkSize[b|B|s|S|k|K|m|M|g|G]
extents LogicalExtentsNumber[%{VG|PVS|FREE|ORIGIN}]
poolmetadatasize MetadataVolumeSize[b|B|s|S|k|K|m|M|g|G]
poolmetadataspare {y|n}
size LogicalVolumeSize[b|B|s|S|k|K|m|M|g|G|t|T|p|P|e|E]
stripesize StripeSize
thin
thinpool ThinPoolLogicalVolume{Name|Path}
virtualsize VirtualSize[b|B|s|S|k|K|m|M|g|G|t|T|p|P|e|E]
wipesignatures {y|n}
zero {y|n}

Example Playbook to call the role
---------------------------------
- hosts: servers roles:
  roles:
  - ../lvcreate

Example of variable values that can be passed
---------------------------------------------
action: create
lvtype: thinpool
extents: 10%FREE
lvname: lvol1
vgname: vg1
pvname: /dev/vdb1
poolname: tp1
virtualsize: 1s
poolmetadatasize: 1k
chunksize: 128K
