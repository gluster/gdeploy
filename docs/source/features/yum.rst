.. _rst_gdeployyum:

yum
^^^

   a. `Install packages`_
   b. `Uninstall packages`_

This module is used to install or remove rpm packages, with the yum module we
can add repos during the install operation.

**If a single configuration has more than one yum section, then the sections
have to be numbered like [yum-1], [yum-2], [yum-3] ...**

1. *action* - This variable allows two values *install* and *remove*.

Install packages
----------------

If the action is install the following options are supported:

1. *packages* - Comma separated list of packages that are to be installed.
2. *repos* - The repositories that have to be added.
3. *gpgcheck* - yes/no values have to be provided.
4. *update* - yes/no; Whether yum update has to be initiated.

For example::

  [yum]
  action=install
  gpgcheck=no
  # Repos should be an url; eg: http://repo-pointing-glusterfs-builds
  repos=<glusterfs.repo>,<vdsm.repo>
  packages=vdsm,vdsm-gluster,ovirt-hosted-engine-setup,screen,gluster-nagios-addons,xauth
  update=yes

Install a package on a particular host::

  [yum:host1]
  action=install
  gpgcheck=no
  packages=rhevm-appliance

Uninstall packages
------------------

If the action is *remove* then only one option has to be provided:

1. *remove* - The comma separated list of packages to be removed.

Unstall a package on a particular host::

  [yum:host1]
  action=remove
  packages=rhevm-appliance
