pvchange
=========
pvchange allows you to change the allocation permissions of one or more physical volumes.

Requirements
------------
Each PhysicalVolume can be a disk partition, whole disk, meta device, or loopback file.

Role Variables
--------------
    disk- disk or partition on which the operation will take place.
    uuid (-u)
    Specify the uuid for the device.Without this option,pvchange generates a
    random uuid.
    metadataignore (--metadataignore) {y|n}
    Ignore or un-ignore metadata areas on this physical volume.
    -x, --allocatable {y|n}
    Enable or disable allocation of physical extents on this physical volume.

Example Playbook to call the role
---------------------------------
    - hosts: servers
      roles:
         - ../pvchange

Example of variable values that can be passed
---------------------------------------------
    action=change
    disk=<disk>
    force=y
    uuid=<uuid>
    metadataignore=y
