pvcreate
=========

pvcreate role initializes  PhysicalVolume for later use by the Logical Volume Manager (LVM).

Requirements
------------
Each PhysicalVolume can be a disk partition, whole disk, meta device, or loopback file.

Role Variables
--------------
    disk- disk or partition on which the pv will be created.
    force (-f)
    Force  the  creation  without  any confirmation.
    uuid (-u)
    Specify the uuid for the device.  Without this option,pvcreate generates a random uuid.
    zero (-Z)
    Whether or not the first 4 sectors of the device should be wiped.
    metadatasize (--metadatasize)
    The approximate amount of space to be set aside for each metadata area.
    dataalignment (--dataalignment)
    Align the start of the data to a multiple of this number.


Example Playbook to call the role
---------------------------------
    - hosts: servers
      roles:
         - ../pvcreate

Example of variable values that can be passed
---------------------------------------------
    action=create
    disks=<disk>
    force=y
    uuid=<uuid>
    dataalignment=1280 
    zero=n
    metadatasize=10

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
