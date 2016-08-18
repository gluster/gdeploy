Installing packages from yum repositories
=========================================

`yum` section allows you to install or remove packages using ``yum`` package manager.

**Note :**

Make sure that  your system is registered with subscription manager before
trying to install packages otherwise you'll get an error while following the
steps below.

**Step 1:**

Create an empty file and give it any arbitrary name. For the purpose of this
demonstration, let's call our file  ``install_packages.conf``. Add the following
lines to your newly created config file::


   # To install package(s):

   # Make sure you have the appropriate values in all the placeholders shown in this configuration file.
   # These values are just for demonstration purposes.

    [yum]
    action=install
    repos=http://jenkins.lab.eng.blr.redhat.com/rhsc/hc/vdsm,http://jenkins.lab.eng.blr.redhat.com/rhsc/hc/glusterfs
    packages=vi,glusterfs
    gpgcheck=no
    update=no

   # Explanation of the above parameters

   # packages
   # --------

   # This takes a comma separate list of values that are packages names you
   # wish to install.
   
   # gpgcheck
   # --------

   # gpgcheck is set to `yes` by default. You can override it 
   # by setting it to `no` as illustrated above.

   # update
   # -------

   # By default,  gdeploy runs `yum update` before installation. To disable
   # this behaviour, set update=no as shown above. The default value is `yes`.

   # To remove package(s):
   # [yum]
   # action=remove
   # packages=vi

**Step 2:**

  As always, to invoke gdeploy run the following command::
  
   $ gdeploy -c install_packages.conf

