.. _rst_gdeployfirewalld:

firewalld
^^^^^^^^^

firewalld module allows the user to manipulate firewall rules. *action* variable
supports two values *add* and *delete*.
Both *add* and *delete* support the following variables:

1. ports/services - The ports or services to add to firewall.
2. permanent - Whether to make the entry permanent. Allowed values are true/false
3. zone - Default zone is public

For example::

  [firewalld]
  action=add
  ports=111/tcp,2049/tcp,54321/tcp,5900/tcp,5900-6923/tcp,5666/tcp,16514/tcp
  services=glusterfs

