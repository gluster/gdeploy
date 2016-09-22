Getting Started
===============

gdeploy works by interacting with the remote nodes by communicating via
passwordless ssh connections. Passwordless ssh connections have to be created to
all the nodes on which gdeploy is going to create and configure a Gluster
volume.

To setup passwordless ssh to the nodes, follow the steps below:

* Generate passphrase-less ssh-keys for the nodes which are to be used with
  gdeploy, running the following command::

    $ ssh-keygen -t rsa -N ''

* Set up passwordless ssh access between the node running gdeploy and servers by
  running the following command::

    $ ssh-copy-id root@hostname

'hostname' refers to the unique IP address of the node.

You would have to run these commands for all the nodes.



Sometimes, you may encounter a “Connection Refused” error. In this case, you
need to check whether the ssh service is running on your system. You may use
this command to check the same::

 $ systemctl status sshd.service

If the service is not running, use this command to start the service::

        $ systemctl start sshd.service

Once ssh connections to all the nodes are established, we can start writing a
configuration file.

That's it! Now the machines are ready to be used with gdeploy.

Invoking gdeploy
^^^^^^^^^^^^^^^^

gdeploy needs a configuration file to run. Write a configuration file, see
`Writing configuration file for gdeploy`_ section below for more details.

Invoke gdeploy with configuration file as an argument::

  $ gdeploy -c sample.conf

Writing configuration file for gdeploy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

gdeploy configuration file is a plain text file comprising multiple sections,
the sections are arranged in an order based on what needs to be achieved.

A very simple configuration file named enable-ntpd.conf which enables and starts
ntpd on all the nodes looks like::

  [hosts]
  10.0.0.1
  10.0.0.2
  10.0.0.3

  [service1]
  action=enable
  service=ntpd

  [service2]
  action=start
  service=ntpd

Invoking gdeploy
^^^^^^^^^^^^^^^^

Invoke gdeploy with configuration file as an argument::

  $ gdeploy -c sample.conf

The configuration file given above will enable and start ntpd on three
nodes. 10.0.0.1, 10.0.0.2, and 10.0.0.3 when the following command is invoked::

  $ gdeploy -c enable-ntpd.conf

INFO: The 'ntp' package has to be installed on both the nodes in order for this
configuration file to run. This can be done using the command "dnf install
ntp".

For more details on the list of all the features supported by gdeploy, refer
`gdeploy features` topic.
