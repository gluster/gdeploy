Role Name
=========
peer_detach

Requirements
------------
1. Nodes that are already probed.
2. glusterd running in all then nodes involved.

Role Variables
--------------
hosts: nodes to be detached.

Example Playbook to call the role.
----------------------------------
    - hosts: servers
      roles:
         - ../roles/peer_detach

Example variables that can be passed.
-------------------------------------
[hosts]
10.70.46.13
10.70.46.15

----------------------------------------------------------------



