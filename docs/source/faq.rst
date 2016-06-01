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

With gdeploy, deployment and configuration is a **lot** easier, it abstracts the
complexities of learning and writing YAML files. And reusing the gdeploy
configuration files with slight modification is lot easier than editing the YAML
files, and debugging the errors.

How does gdeploy help in setting up GlusterFS clusters?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Setting up a GlusterFS volume involves quite a bit of tasks like:
1. Setting up PV, VG, LV (thinpools if necessary).
2. Peer probing the nodes.
3. And a CLI to create volume (which can get lengthy and error prone as the
number of nodes increase).

gdeploy helps in simplifying the above tasks and adds many more useful features
like installing packages, handling volumes remotely, setting volume options
while creating the volume so on...

Does gdeploy help in installing GlusterFS packages?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes. gdeploy has feature to register to subscription manager and features to use
yum via the configuration file. User can install GlusterFS packages either from
Red Hat channels or from upstream builds.

Is gdeploy only for installing and deploying GlusterFS?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

No. With gdeploy user can install any package and user shell and script modules
to configure them. Refer `hc.conf
<https://github.com/gluster-deploy/gdeploy/blob/2.0/examples/hc.conf>`_ for an
example for things gdeploy can achieve.


Can I run arbitrary scripts using gdeploy?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes. See the *script* module. Refer `hc.conf
<https://github.com/gluster-deploy/gdeploy/blob/2.0/examples/hc.conf>`_ for an
example for script module usage.

My gdeploy run is failing with Module Error, why?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The error is due to the Ansible version installed. This is possibly because you
might be using Ansible 2.0. gdeploy currently supports 1.9.x versions of
Ansible.
