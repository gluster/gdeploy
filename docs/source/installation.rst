Installation
============

Prerequisites
^^^^^^^^^^^^^

gdeploy requires the following packages:

* Python 2.x
* Ansible 1.9.x (*Note that gdeploy is not compatible with Ansible 2.x*)
* python-argparse
* PyYAML
* Jinja2

Installing Ansible
^^^^^^^^^^^^^^^^^^

Follow instructions in the Ansible documentation on how to install Ansible,
which can be found `here
<http://docs.ansible.com/ansible/intro_installation.html>`_.

Installing gdeploy
^^^^^^^^^^^^^^^^^^^

gdeploy can be installed using pre-built RPM or can be installed from source.

Installing from RPM
~~~~~~~~~~~~~~~~~~~

Latest version of gdeploy RPMs can be downloaded from `here
<http://download.gluster.org/pub/gluster/gdeploy/LATEST>`_ and installed ::

  Using yum:
  $ sudo yum install ./gdeploy-<version>-<release>.rpm

  Using dnf:
  $ sudo dnf install ./gdeploy-<version>-<release>.rpm


Installing from source
~~~~~~~~~~~~~~~~~~~~~~

Alternatively gdeploy can be installed from source ::

   $ git clone git@github.com:gluster/gdeploy.git
   $ cd gdeploy

Make sure you have gcc and python-devel installed ::

   $ sudo yum install gcc python-devel
   $ sudo pip install -r requirements.txt


Setup gdeploy

Run the gdeploy_setup.sh file from the root directory of gdeploy ::

  $ cd gdeploy
  $ sudo ./gdeploy_setup.sh

**OR Setup manually as follows**

1. Add ansible modules to ANSIBLE_LIBRARY environment variable ::

   $ echo "export ANSIBLE_LIBRARY=$ANSIBLE_LIBRARY:/path/to/gdeploy/modules/" >> ~/.bashrc

2. Add ansible playbooks(inside the templates directory) to GDEPLOY_TEMPLATES
   environment variable ::

     $ echo "export GDEPLOY_TEMPLATES='path/to/gdeploy'" >> ~/.bashrc
     $ source ~/.bashrc

3. Install gdeploy using setuptools ::

     $ sudo python setup.py install
