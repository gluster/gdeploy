pvremove
=========
pvremove wipes the label on a device so that LVM will no longer recognise it as a physical volume.

Requirements
------------
Existing PhysicalVolume on the disk mentioned.

Role Variables
--------------
    disks - disk or partition from which the PhysicalVolume will be removed. 
    force (-f) Force  the  creation  without  any confirmation.

Example Playbook to call the role
---------------------------------
    - hosts: servers
      roles:
         - ../pvremove

Example of variable values that can be passed
---------------------------------------------
             action= remove
             disks=/dev/vdb1
             force=y

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
