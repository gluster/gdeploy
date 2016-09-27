.. _rst_gdeployshell:

shell
^^^^^

shell module allows user to run shell commands on the remote nodes.

Currently shell provides a single *action* variable with value *execute*. And a
*command* variable with any valid shell command as value.

The below config will execute vdsm-tool on all the nodes::

  [shell]
  action=execute
  command=vdsm-tool configure --force

Refer `hc.conf
<https://github.com/gluster-deploy/gdeploy/blob/2.0/examples/hc.conf>`_ for
complete example.
