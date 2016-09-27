.. _rst_subscriptionmanagement:

Subscription Manager
^^^^^^^^^^^^^^^^^^^^

   a. `Register`_
   b. `Unregister`_
   c. `Enable`_
   d. `Disable`_
   e. `Attach pools`_



This module is used to subscribe/unsubscribe to channels, attach a pool, enable
repos etc. Subscription Manager module is named RH-subscription
The RH-subscription module allows the following variables:

  1. action - This variable allows the following values, *register*,
     *attach-pool*, *enable-repos*, *disable-repos*, *unregister*.


Register
--------
If the action is *register* the following options are supported:

1. username/activationkey - Username or activationkey
2. password/actiavtionkey - Password or activation key
3. auto-attach - true / false
4. pool - Name of the pool
5. repos - Repos to subscribe to
6. disable-repos - Repo names to disable. Leaving black will disable all the
   repos

For example::

  [RH-subscription1]
  action=register
  username=user@user.com
  password=<passwd>
  pool=<pool>


Unregister
----------
If the action is *unregister* the systems will be unregistered.


Enable
------
If the action is *enable-repos* the following options are supported:

1. repos - List of comma separated repos that are to be subscribed to.

Disable
-------
If the action is *disable-repos* the following options are supported:

1. repos - List of comma separated repos that are to be subscribed to.

Attach pools
------------
If the action is *attach-pool* the following options are supported:

1. pool - Pool name to be attached.

Refer `hc.conf
<https://github.com/gluster-deploy/gdeploy/blob/2.0/examples/hc.conf>`_ for
complete example.
