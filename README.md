# gdeploy deprecation Notice
The authors and maintainers would be freezing the development 
of gdeploy and would be focusing on [gluster-ansible](https://github.com/gluster/gluster-ansible) project. 
There would be no further feature development. However the existing code base would have 
community support till the lifecycle of Gluster 3.x series (Bugfixes only). 
The gdeploy-2.0.9 would be the last release avaialable. 

**Gluster - 4.0 and beyond :**
We are pushing all the existing modules to upstream ansible project 
and would be available as storage module within Ansible project.
The deployment stratergy would be an Ansible Role.

**Distributions :**
Both the FedoraProject and CentOS would be shipping the 
gdeploy-2.0.9 RPMS for gluster Project for the 3.x series 
and would be community supported.

# gdeploy release 2.0

These are gdeploy 2.0 release notes. Lists the features and changes introduced
in 2.0.

## What is gdeploy?

  gdeploy is a tool to set-up and deploy [GlusterFS](https://www.gluster.org) using [Ansible](https://www.ansible.com) over multiple
  hosts. gdeploy is written to be modular, it can be used to deploy any
  software depending on how the configuration file is written.

  gdeploy can be used to set-up bricks for GlusterFS, create a GlusterFS volume
  and mount it on one or more clients from an ansible installed machine. The
  framework reads a configuration file and applies on the hosts listed in the
  configuration file.
  
  You can find instructions [here](https://github.com/gluster/gdeploy/blob/master/docs/INSTALL.md).

## What is new in 2.0?

   - Multiple volume support, now one can create multiple volumes in a single
     configuration file.
   - Adds support to create volume and set volume options in the same section.
   - More developer friendly, now adding a new feature/module is much easier.
   - Support to run shell scripts on remote hosts. gdeploy configuration file
     allows provision to mention the shell script which will be copied and run
     on the remote host.
   - Support for gluster features like quota, snapshot...
   - Adds configurable option to reserve space for snapshots while creating
     logical volumes.
   - Adds Subscription-manager support.
   - yum module support.
   - firewalld module support.
   - Improvement to configuration file:
     - Now the sections can be written like: [module:host]
       > Example: [backend-setup:10.0.0.10] ...
     - Multiple invocation of modules. 
       > Example: [shell1], [shell2] for multiple shell invocations.
   - Bug fixes.

## Get involved

   - Read [developer guide](https://github.com/gluster/gdeploy/blob/master/docs/developer-guide.md)
   - All code submissions are done through pull requests.
   - irc: #gdeploy (Freenode)

## Licence
GNU Click on the [link](https://github.com/gluster/gdeploy/blob/master/LICENSE) to see the full text.
