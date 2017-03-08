.. _rst_gdeploysnapshot:

Snapshot
^^^^^^^^

*snapshot* module enables user to create point-in-time copies of Rhgs volumes.

Snapshot provides the following actions:

   a. `Create`_
   b. `Delete`_
   c. `Activate`_
   d. `Deactivate`_
   e. `Clone`_
   f. `Restore`_
   g. `Config`_

action - This variable allows the following values, *create*, *delete*,
         *activate*, *deactivate*, *clone*, *restore*, *config*.


Create
------
If the action is *create* the following variables are supported:
1. snapname - Name of the snapshot that will be created.
2. volname - Name of the volume for which the snapshot will be created.
3. force - Snapshot creation will fail if any brick is down. Quorum is checked
           only when the force option is provided.
           The default value for this field is 'no'.

Example 1: Creating a snapshot::

  [snapshot]
  action=create
  snapname=snap_Feb2017
  volname=snapvol
  force=yes


Delete
------
If the action is *delete* the following variables are supported:
1. snapname
2. volname
3. force

Example 2: Deleting a snapshot::

    [snapshot]
    action=delete
    snapname=snap_Dec2016
    volname=snapvol

Activate
--------
If the action is *activate* the following options are supported:
1. snapname
2. force

Example 3: Activate a Snapshot::

  [snapshot]
  action=activate
  snapname=snap_Feb2017
  force=yes

Deactivate
----------
If the action is *deactivate* the following options are supported:
1. snapname
2. force

Example 4: Deactivate a Snapshot::

  [snapshot]
  action=deactivate
  snapname=snap_Jan2017
  force=yes

Clone
-----
If the action is *clone* the following options are supported:
1. snapname
2. force
3. clonename - The name of the clone, ie, the new volume that will be created.

Example 5: Clone a Snapshot::

  [snapshot]
  action=clone
  snapname=snap_Nov2014
  clonename=snap_clone

Restore
-------
If the action is *restore* the following options are supported:
1. snapname

Example 5: Restore a Snapshot::

  [snapshot]
  action=restore
  snapname=snap_Jan2017

Config
------
If the action is *config* the following options are supported:
1. snapname - Nmae of the snapshot that will be created.
2. snap_max_soft_limit - This is a percentage value. The default value is 90%.
3. snap_max_hard_limit - If the snapshot count in a volume reaches this limit
                         then no further snapshot creation is allowed. The range
                         is from 1 to 256.
4. auto_delete - By default it is disabled. When enabled, it will delete the
                 oldest snapshot when snapshot count crosses snap_max_soft_limit. 
5. activate_on_create - 

Example 5: Configure a Snapshot::

  [snapshot]
  action=config
  snapname=snap_Feb2017
  snap_max_hard_limit=200
  auto_delete=enable
