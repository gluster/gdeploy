.. _rst_subscriptionmanagement:

Subscription Manager
^^^^^^^^^^^^^^^^^^^^

Red Hat Subscription Manager is a local service which tracks installed products
and subscriptions on a local system to help manage subscription assignments. It
communicates with the backend subscription service (the Customer Portal or an
on-premise server such as Subscription Asset Manager) and works with content
management tools such as yum.

This section explains the gdeploy module `RH-subscription', which can be used to
configure subscription manager.

RH-subscription provides the following actions:

   a. `Register`_
   b. `Unregister`_
   c. `Enable`_
   d. `Disable`_
   e. `Attach pools`_

action - This variable allows the following values, *register*, *attach-pool*,
         *enable-repos*, *disable-repos*, *unregister*.


Register
--------
If the action is *register* the following variables are supported:

1. username/activationkey - Username or activationkey
2. password/actiavtionkey - Password or activation key
3. auto-attach - true / false, if set to true subscription manager looks for
   product certificates in /etc/pki/product/
4. pool - Name of the pool to be attached
5. repos - Repos to subscribe to
6. disable-repos - Repo names to disable. Leaving blank will disable all the
   repos
7. ignore_register_errors: If set to no, gdeploy will exit if system
   registration fails.

Example 1: Register to Red Hat subscription management::

  [RH-subscription]
  action=register
  username=user@user.com
  password=<passwd>
  pool=<pool>

Unregister
----------
If the action is *unregister* the systems will be unregistered from RHSM.

Example: Unregister the system::
    [RH-subscription]
    action=unregister

Enable
------
If the action is *enable-repos* the following options are supported:

1. repos - List of comma separated repos that are to be subscribed to.
2. ignore_enable_errors - If set to no, gdeploy fails if enable-repos fail.

Example 2: Enable repositories::

  [RH-subscription]
  action=enable-repos
  repos=rhel-7-server-rpms,rh-gluster-3-for-rhel-7-server-rpms

Disable
-------
If the action is *disable-repos* the following options are supported:

1. repos - List of comma separated repos that are to be subscribed to.

Attach pools
------------
If the action is *attach-pool* the following options are supported:

1. pool - Pool name to be attached.
2. ignore_attach_pool_errors - If set to no, gdeploy fails if attach-pool
   fails.

attach-pool can be initiated at the time of registration.

Refer `hc.conf
<https://github.com/gluster-deploy/gdeploy/blob/2.0/examples/hc.conf>`_ for
complete example.
