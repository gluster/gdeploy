.. _rst_gdeploysystemd:

systemd
^^^^^^^

   a. `Enable Service`_
   b. `Disable Service`_
   c. `Start Service`_
   d. `Stop Service`_
   e. `Restart Service`_

[service] module in gdeploy adds systemd support. The *service* module allows
user to *start*, *stop*, *restart*, *reload*, *enable*, or *disable* a
service. The action variable specifies these values.

Enable Service
--------------

When the *action* variable is set to *enable* the *service* variable has to be
set. For example::

  [service]
  action=enable
  service=ntpd


Disable Service
---------------

When the *action* variable is set to *enable* the *service* variable has to be
set. For example::

  [service]
  action=enable
  service=ntpd


Start Service
-------------

When the *action* variable is set to *start* the *service* variable has to be
set. For example, below configuration starts the ntpd service ::

  [service]
  action=start
  service=ntpd


Stop Service
------------

When the *action* variable is set to *stop* the *service* variable has to be
set. For example::

  [service]
  action=stop
  service=ntpd


Restart Service
---------------

When the *action* variable is set to *restart* the *service* variable has to be
set. For example::

  [service]
  action=restart
  service=ntpd

