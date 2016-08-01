Installing packages from yum repositories
=========================================

`yum` section allows you to install or remove packages using ``yum`` package manager.

**Note :**

Make sure that  your system is registered with subscription manager before
trying to install packages otherwise it will throw error.

**Step 1:**

Create an empty file and give it any arbitrary name. For the purpose of this
demonstration, let's call our file ``install_packages.conf``. Add the following
lines to your newly created config file::


   # To install package(s):
   # Make sure you have the appropriate values in all the placeholders shown in this configuration file.
   # These values are just for demonstartion purposes.

    [yum]prerequistet
    action=install
    repos=http://jenkins.lab.eng.blr.redhat.com/rhsc/hc/vdsm,http://jenkins.lab.eng.blr.redhat.com/rhsc/hc/glusterfs
    packages=vi,glusterfs
    gpgcheck=no
    update=no


   # If gpgcheck is set to `no`, gpgcheck will be disabled. By default
   # it is 'yes'.
   #
   # If 'no' provided to update, gdeploy will not run  'yum update' before
   # installation. By default  it is 'yes'.

   # To remove package(s):
   # [yum]
   # action=remove
   # packages=vi

**Step 2:**

  Invoke gdeploy and run the following command::
  
   $ gdeploy -c install_packages.conf


