.. _rst_gdeployquota:

quota
^^^^^

*quota* module allows user to set limits on the disk space used by a directory.
Storage admins can control the disk space utilization at the directory and
volume levels.

The 'action' option can be any of the following:
1. enable - To enable quota behavior on a volume.
2. disable - To disable quota behavior on a volume.
3. remove - To remove the usage limits, if previously set.
4. remove-objects -To remove the usage limits on a specific directory, if
                   previously set.
5. default-soft-limit - The default soft limit is 80%, though it can be altered
                        on a per-volume basis.
6. limit-usage - To limit the total amount of space to be consumed by a volume.
7. limit-objects - To limit the total allowed number of directories/files.
8. alert-time - To configure how frequently usage information is logged.
                By default alert-time is 1 week(1w).
9. soft-timeout - To specify how often disk usage is to be checked against the
                  disk usage limit when below the soft limit set on the directory
                  or volume. The default soft timeout frequency is every 60 seconds.
10. hard-timeout - To specify how often disk usage is to be checked against the
                  disk usage limit when above the soft limit set on a directory
                  or volume. The default hard timeout frequency is every 5 seconds.

All of the above options support the following variables:
* *volname* - This option specifies the volume name.

* *path* - remove, remove-objects, limit-usage and limit-objects option support
           *path* variable to specify the path of the directory.
* *size* - limit-usage option supports a *size* variable to specify the size of
           the disk to be used.
* *number* - limit-objects option supports the *number* variable to specify the
             maximum number of directories/files.
* *percent* - default-soft-limit supports a *percent* variable to specify the
              percentage of the disk space supposed to be used.
* *time* - alert-time, soft-timeout, and hard-timeout support the *time* variable
           to specify the time in weeks,seconds and seconds respectively.
* *client_hosts* - soft-timeout and hard-timeout options support the *client_hosts*
                   variable


For example::

Example 1: Enable quota on a specific volume::

  [quota]
  action=enable
  volname=quotavol

Example 2: Limit the disk-usage for the specific volume::

  [quota]
  action=limit-usage
  volname=quotavol
  path=/mnt
  size=100GB

Example 3: Limit the number of files for a specific volume::

  [quota]
  action=limit-objects
  volname=quotavol
  number=3

Example 4: Set soft-timeout for quotavol volume::

  [quota]
  action=soft-timeout
  time=90
