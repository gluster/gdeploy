Usage
=====

gdeploy needs a configuration file to do anything useful. Refer
:ref:`rst_writingconfig` for an example.

gdeploy -h will list the available options for gdeploy::

  $ gdeploy -h
  usage: gdeploy [-h] [-v] [-vv] [-c CONFIG_FILE] [-k]

  optional arguments:
    -h, --help            show this help message and exit
    --version             show program's version number and exit
    -c CONFIG_FILE        Configuration file
    -k                    Keep the generated ansible utility files
    --trace               Turn on the trace messages in logs
    -vv                   verbose mode
    --addfeature FEATURE_NAME
                          Add new feature to gdeploy


gdeploy --addfeature FEATURE_NAME will create a skeleton to add a new feture to
gdeploy. For more details on how to write a feature refer
:ref:`rst_developerdoc`.

Invoke gdeploy with configuration file as an argument::

  $ gdeploy -c config-file

More example configuration files can be found `here
<https://github.com/gluster/gdeploy/tree/master/examples>`_.
