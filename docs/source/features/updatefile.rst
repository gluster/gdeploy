.. _rst_gdeployupdatefile:

Updating a file
^^^^^^^^^^^^^^^

*update-file* module allows user to copy a file, edit a line in a file, or add
new lines to a file. action variable can be any of *copy*, *edit*, or *add*.

When the *action* variable is set to *copy*, the following variables are
supported.

1. src - The source path of the file to be copied from.
2. dest - The destination path on the remote machine to where the file is to be
   copied to.

When the *action* variable is set to *edit*, the following variables are
supported.

1. dest - The destination file name which has to be edited.
2. replace - A regular expression, which will match a line that will be replaced.
3. line - Text that has to be replaced.

When the *action* variable is set to *add*, the following variables are
supported.

1. dest - File on the remote machine to which a line has to be added.
2. line - Line which has to be added to the file. Line will be added towards the end of the file.

Example 1: Copy a file to a remote machine ::

  [update-file]
  action=copy
  src=/tmp/foo.cfg
  dest=/etc/nagios/nrpe.cfg


Example 2: Edit a line in the remote machine, in the below example lines that
have allowed_hosts will be replaced with allowed_hosts=host.redhat.com ::

  [update-file]
  action=edit
  dest=/etc/nagios/nrpe.cfg
  replace=allowed_hosts
  line=allowed_hosts=host.redhat.com

Example 3: Add a line to the end of a file ::

  [update-file]
  action=add
  dest=/etc/ntp.conf
  line=server clock.redhat.com iburst
