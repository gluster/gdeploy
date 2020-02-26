#Installation

###Clone this repo:

` git clone git@github.com:gluster/gdeploy.git`

` cd gdeploy`

###Install the requirements:

 Make sure you have gcc and python-devel installed

 `yum install gcc python-devel`

` pip install -r requirements.txt`

 python-setuptools is needed to run setup.py, lookup specific pacakage in your
 distribution and install it.

 If [backend-setup] or any other lvm releated sections are used, ensure to
 install lvm2 package.

###Setup GDeploy

**Run the gdeploy_setup.sh file from the root directory of gdeploy**

` ./gdeploy_setup.sh`

***OR***

**Setup manually as follows**

1. Add ansible modules to ANSIBLE_LIBRARY environment variable
<br/>` echo "export ANSIBLE_LIBRARY=$ANSIBLE_LIBRARY'/path/to/gdeploy/modules/'" >> ~/.bashrc`<br/>
2. Add ansible playbooks(inside the templates directory) to GDEPLOY_TEMPLATES environment variable
<br/>` echo "export GDEPLOY_TEMPLATES='path/to/gdeploy'" >> ~/.bashrc`<br/>
3. Install glusterlib module using setuptools
<br/>` python setup.py install`<br/>


##Usage

To use the framework create a configuration file as per your needs.
Follow the instructions [here](https://github.com/gluster/gdeploy/blob/master/examples/gluster.conf.sample)
to create your configuration file.
An example configuration file can be found [here](//github.com/gluster/gdeploy/tree/master/examples)

See gdeploy.conf(5) manpage for more details.

To set-up back-end and deploy GlusterFS in the specified host machines, run:

` gdeploy -c <configuration file>`

For help and usage options, try:

` gdeploy -h`
