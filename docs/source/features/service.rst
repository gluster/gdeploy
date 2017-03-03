.. _rst_gdeployservice:

Service
^^^^^^^

*service* module allows user to start, stop, restart, reload, enable, or disable
a service.
When 'action' variable is set to any of *start*, *stop*, *restart*, *reload*,
*enable*, *disable* the variable servicename specifies which service to start,
stop etc.
All of the above options support variables 'service' and 'ignore_service_errors'.
service - Name of the service to start, stop etc.
ignore_service_errors - default value for this variable is 'yes'.

For example::

Enable and start ntp daemon::

  [service1]
  action=enable
  service=ntpd

  [service2]
  action=restart
  service=ntpd