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
    disks=/dev/vdb1
    force=y
    uuid=92aa09de-7680-11e7-b5a5-be2e44b06b34
    metadataignore=y


License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
