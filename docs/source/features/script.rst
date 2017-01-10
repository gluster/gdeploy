.. _rst_gdeployscript:

script
^^^^^^

script module enables user to execute a script/binary on the remote
machine. action variable is set to execute. Allows user to specify two variables
*file* and *args*.

1. file - An executable on the local machine.
2. args - Arguments to the above program.

Example: Execute script disable-multipath.sh on all the remote nodes listed in *hosts* section::

  [script]
  action=execute
  file=/usr/share/gdeploy/scripts/disable-multipath.sh

Refer `hc.conf
<https://github.com/gluster-deploy/gdeploy/blob/2.0/examples/hc.conf>`_ for a
complete example.
