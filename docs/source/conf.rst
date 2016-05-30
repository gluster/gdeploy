Configuration File and gdeploy Features
=======================================

This section explains the gdeploy configuration file format, and the available
features. There is no rule to name the configuration files in gdeploy as long as
the file name is mentioned with *-c* option for gdeploy. For example
gluster.conf, gluster, gluster.txt, gluster.config are all valid names for a
gdeploy configuration file.

gdeploy configuration file is split into two parts.

1. Inventory
2. Features

**1. Inventory**

The section is named [hosts], this is a mandatory section, hosts that are to be
configured have to be listed in this section.

Hostnames or ip addresses have to be listed one per line. For example::

  [hosts]
  10.0.0.1
  10.0.0.2
  10.0.0.3

**2. Features**

gdeploy supports a lot of features, a comprehensive list can be found in the
sample file `here
<https://github.com/gluster/gdeploy/blob/master/examples/gluster.conf.sample>`_.
And more examples can be found `here
<https://github.com/gluster/gdeploy/tree/master/examples>`_.

gdeploy was initially written to create and configure GlusterFS volumes, now it
supports more features than just creating and configuring GlusterFS
volumes. The following are the features supported:

1. LVM Support

   a. Creating PV
   b. Creating VG
   c. Creating LV

2. Subscription Manager Support

   a. Register
   b. Unregister
   c. Enable
   d. Disable
   e. Attach pools

3. yum Support

   a. Install packages
   b. Uninstall packages
   c. Add a repo

4. systemd Support

   a. Enable service
   b. Disable
   c. Start
   d. Stop

5. Shell Module

6. Script Module

7. SELinux Support

8. FirewallD Support

9. Updating a file

10. Creating Volumes
