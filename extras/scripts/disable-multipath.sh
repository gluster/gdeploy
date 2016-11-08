#!/usr/bin/env bash -eu
#
# stop and disable multipathd (the daemon) *and* blacklist all device names like 
# /dev/sda so they do not appear in the output of multipath (the CLI)
#
#

warn(){
echo <<\EOF >&2
 this script will prevent listing iscsi devices when multipath CLI is called
without parameters, and so no LUNs will be discovered by applications like VDSM
(oVirt, RHV) which shell-out to call `/usr/sbin/multipath` after target login
EOF
}

# warn if disabling multipath will disable iSCSI discovery in oVirt, etc...
# returns errexit=0 if there is at least one session
which iscsiadm >/dev/null && \
  iscsiadm --mode session >/dev/null && \
    WARN="true"
# test if VDSM is installed
test -d /etc/vdsm && WARN="true"

# warn if true
[[ ${WARN:=false} == "true" ]] && warn

multipath -F
systemctl stop multipathd
systemctl disable multipathd

# insert blacklist unless exists
grep "inserted by $0" /etc/multipath.conf >/dev/null && \
  exit 0
cat <<EOF>> /etc/multipath.conf
# inserted by $0
blacklist {
        devnode "*"
}
EOF

