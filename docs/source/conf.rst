.. _rst_writingconfig:

Configuration file format
=========================

This section explains the gdeploy configuration file format. There is no rule to
name the configuration files in gdeploy as long as the file name is mentioned
with *-c* option for gdeploy. For example gluster.conf, gluster, gluster.txt,
gluster.config are all valid names for a gdeploy configuration file.

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

There can be more than one feature listed in the configuration file, each
separated by a newline. Every feature section has one or more variables which
controls how the feature is configured/deployed. The below example has two
features, firewalld and service that will be configured on all the hosts listed
in the [hosts] section::

  [hosts]
  10.0.0.1
  10.0.0.2
  10.0.0.3
  10.0.0.4

  [firewalld]
  action=add
  ports=111/tcp,2049/tcp,54321/tcp
  permanent=true
  zone=public

  [service1]
  action=enable
  service=ntpd

  [service2]
  action=restart
  service=ntpd

If a feature has to be used more than once, then it has to be in different
sections and numbered to make it unique as shown in the above example.

The list of available features and their complete documentation can be found in
:ref:`rst_gdeployfeatures` page.
