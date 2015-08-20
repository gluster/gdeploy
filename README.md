#gdeploy

Tool to set-up and deploy glusterfs using ansible over multiple hosts

gluster-deploy can be used to set-up the back-end, create a glusterfs volume
and mount it to a client over n-number of clients from an ansible installed
machine. The framework takes the configurations for this from a configuration
file to be defined by the user.


##Installation

###Clone this repo:

` git clone git@github.com:gluster/gdeploy.git`

` cd gdeploy`

###Install the requirements:

` pip install -r requirements.txt`

###Add ansible modules to ANSIBLE_LIBRARY environment variable

` echo "export ANSIBLE_LIBRARY=$ANSIBLE_LIBRARY:'/path/to/gdeploy/modules/'" >> ~/.bashrc`

###To use the module you can either do:

####Install using setuptools:

` python setup.py install`

OR

####Add the path to the module to the python path:

` echo "export PYTHONPATH=$PYTHONPATH:'/path/to/gdeploy/glusterlib/'" >> ~/.bashrc`



##Usage

To use the framework create a configuration file as per your needs.
Follow the instructions [here](https://github.com/nandajavarma/gdeploy/tree/master/examples/README.md)
to create your configuration file.
An example configuration file can be found [here](//github.com/nandajavarma/gdeploy/tree/master/examples)

> TODO: better README for the configuration file

To set-up back-end and deploy GlusterFS in the specified host machines, run:

` gdeploy -c <configuration file>`

For help and usage options, try:

` gdeploy -h`

