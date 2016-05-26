Getting Started
===============

gdeploy works by interacting with the remote nodes by communicating via
passwordless ssh connections. Passwordless ssh connections have to be setup to
all the nodes from where gdeploy is run.

To setup passwordless ssh to the nodes, follow the steps below:

* Generate passphrase-less ssh-keys for the nodes which are to be used with
  gdeploy, running the following command::

    $ ssh-keygen -t rsa -N ''

* Set up passwordless ssh access between the node running gdeploy and servers by
  running the following command::

    $ ssh-copy-id root@hostname

That's it! Now the machines are ready to be used with gdeploy.

Invoking gdeploy
^^^^^^^^^^^^^^^^

gdeploy needs a configuration file to run. Write a configuration file, see
`Writing configuration file for gdeploy`_ section below for more details.

Invoke gdeploy with configuration file as an argument::

  $ gdeploy -c sample.conf

Writing configuration file for gdeploy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

gdeploy configuration file is made up of multiple sections, the sections are
arranged in an order based on what needs to be achieved.

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

The above file will enable and start ntpd on three nodes. 10.0.0.1, 10.0.0.2,
and 10.0.0.3 when the following command is invoked::

  $ gdeploy -c enable-ntpd.conf

For more details on the list of all the features supported by gdeploy, refer
`gdeploy features` topic.

