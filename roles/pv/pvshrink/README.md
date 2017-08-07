pvshrink
=========
pvshrink shrinks PhysicalVolume which may already be in a volume group and have active logical volumes allocated on it.

Requirements
------------
Existing PhysicalVolume on the disk mentioned.

Role Variables
--------------
    disk- disk or partition on which the pv will be shrunk.
    setphysicalvolumesize (--setphysicalvolumesize)
    Overrides the automatically-detected size of the PV.  Use with care, or prior to reducing the physical size of the device.

<!-- Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles. -->

Example Playbook to call the role
---------------------------------
    - hosts: servers
      roles:
         - ../pvshrink

Example of variable values that can be passed
---------------------------------------------
      action=resize
      disks=/dev/vdb1
      setphysicalvolumesize=1G

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
