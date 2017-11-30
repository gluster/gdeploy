Role Name
=========

peer_probe - Probe a list of peers into a cluster.

Requirements
------------

This role requires glusterfs_peer module to be present.

Role Variables
--------------

This role requires the `nodes' variable to be set.

Dependencies
------------

None

Example Playbook
----------------

    - hosts: master
      tasks:
      - include_role:
           name: glusterfs/peer_probe
        vars:
          nodes:
                - 10.70.43.142
                - 10.70.43.200
                - 10.70.42.69


License
-------

GPLv3

Author Information
------------------

Sachidananda Urs <surs@redhat.com>
