.. _rst_gdeploypeer:

Peer
^^^^

*peer* module allows user to add/probe remote machines to a Trusted Storage Pool,
detach/remove a remote machine from a Trusted Storage Pool.
action variable can be any of *probe*, *detach*, or *ignore*.

When the *action* variable is set to *probe*, the remote machines listed in the
hosts sections are added to the Trusted Storage Pool.

When the *action* variable is set to *detach*, the remote machines listed in the
hosts sections are removed from the Trusted Storage Pool.
The option detach also supports a force variable that can be set to 'yes', the
default value is 'no' for the same.

Both probe and detach support ignore_peer_errors variable that can be set to 'no',
its default value is 'yes'.


Example 1: Add the specified hosts to a Trusted Storage Pool ::

  [peer]
  action=probe

Example 2: Add the specified hosts to a Trusted Storage Pool, in the below
example the errors will not be ignored. ignore_peer_errors has 'yes' as its default value ::

  [peer]
  action=probe
  ignore_peer_errors=no

Example 3: Detach a host from the Trusted Storage Pool ::

  [peer]
  action=detach
  force=yes
