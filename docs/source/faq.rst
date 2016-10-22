Frequently Asked Questions
==========================

1. `Why do we need gdeploy, when Ansible is available?`_
2. `How does gdeploy help in setting up GlusterFS clusters?`_
3. `Does gdeploy help in installing GlusterFS packages?`_
4. `Is gdeploy only for installing and deploying GlusterFS?`_
5. `Can I run arbitrary scripts using gdeploy?`_
6. `My gdeploy run is failing with Module Error, why?`_


Why do we need gdeploy, when Ansible is available?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

gdeploy enables configuration and provisioning of GlusterFS and the file access protocols using configurations and tunables which are tested and recommended by the maintainers. This enables a system administrator to have an easy way to create consistent and repeatable deployment paths.


How does gdeploy help in setting up GlusterFS clusters?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Installation, configuration and provisioning of a GlusterFS deployment involves a sequence of steps to be executed in the proper order. This would include deployment-specific detail such as:

1. Setting up PV, VG, LV (thinpools if necessary).
2. Peer probing the nodes.
3. Using the CLI based volume creation steps

gdeploy provides a simple way to complete the steps and include specifics such as configuring volume options and such.


Does gdeploy help in installing GlusterFS packages?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

gdeploy has a configuration workflow design which enables it to be used for package installation, either from upstream builds or, from a specific vendor provided content distribution mechanism viz. Red Hat's CDN


Is gdeploy only for installing and deploying GlusterFS?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

While gdeploy is intended to streamline the administrator experience during installation and deployment of GlusterFS, it can be used to install other packages, custom scripts and modules for configuration. The hc.conf is an example of how gdeploy can enable the set-up and configuration for a HyperConverged stack using GlusterFS.

Refer `hc.conf
<https://github.com/gluster-deploy/gdeploy/blob/2.0/examples/hc.conf>`_ for an
example for things gdeploy can achieve.


Can I run arbitrary scripts using gdeploy?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes. Scripts which aid and extend the deployment setup can be configured to run from gdeploy.

See the *script* module. Refer `hc.conf
<https://github.com/gluster-deploy/gdeploy/blob/2.0/examples/hc.conf>`_ for an
example for script module usage.

My gdeploy run is failing with Module Error, why?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The error is due to the Ansible version installed. This is possibly because you
might be using Ansible 2.0. gdeploy currently supports 1.9.x versions of
Ansible.
