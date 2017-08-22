Role Name
=========
peer_probe

Requirements
------------
1. Passwordless ssh connection established between nodes. 
2. glusterd running
3. All nodes should be up and running.

Role Variables
--------------
hosts: nodes to be probed.

Example Playbook to call the role.
----------------------------------
    - hosts: servers
      roles:
         - ../roles/peer_probe

Example variables that can be passed.
-------------------------------------
[hosts]
10.70.46.13
10.70.46.15

----------------------------------------------------------------



