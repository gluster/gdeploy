#gdeploy

[![Build Status](https://travis-ci.org/gluster/gdeploy.svg?branch=test)](https://travis-ci.org/gluster/gdeploy)

Tool to set-up and deploy GlusterFS using ansible over multiple hosts.

gdeploy can be used to set-up the backend, create a GlusterFS volume
and mount it on one or more clients from an ansible installed machine.
The framework reads a configuration file and applies on the hosts listed
in the configuration file.

