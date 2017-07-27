                gdeploy release 2.0

These are gdeploy 2.0 release notes. Lists the features and changes introduced
in 2.0.

What is gdeploy?

  gdeploy is a tool to set-up and deploy GlusterFS using ansible over multiple
  hosts. gdeploy is written to be modular, it can be used to deploy any
  software depending on how the configuration file is written.

  gdeploy can be used to set-up bricks for GlusterFS, create a GlusterFS volume
  and mount it on one or more clients from an ansible installed machine. The
  framework reads a configuration file and applies on the hosts listed in the
  configuration file.

What is new in 2.0?

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
     - Now the sections can be written like:
       [module:host], for e.g: [backend-setup:10.0.0.10] ...
     - Multiple invocation of modules. For eg: [shell1], [shell2] for multiple
       shell invocations.
   - Bug fixes.

