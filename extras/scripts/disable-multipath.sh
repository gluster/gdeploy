#!/usr/bin/env bash
#
# stop and disable multipathd (the daemon) *and* blacklist all device names like 
# /dev/sda so they do not appear in the output of multipath (the CLI)
#

# shell exit with error (errexit) if any command returns exit != 0 or any variable
# is undefined (nounset)
set -ue

MULTIPATH_CONF='/etc/multipath.conf'

warn(){
cat <<\EOF >&2
This script will prevent listing iscsi devices when multipath CLI is called
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

# Load the multipath module before trying to flush
# modprobe multipath
modprobe dm_multipath

# flush maps; script will exit with error if map in use
multipath -F

# insert wildcard blacklist for all device names unless exists
BASENAME=$(basename $0)
grep "inserted by $BASENAME" $MULTIPATH_CONF >/dev/null && \
  exit 0
cat <<EOF>> $MULTIPATH_CONF
# inserted by $BASENAME

blacklist {
        devnode "*"
}
EOF

# Insert these lines to the beginning of the file, if they are not present
if grep -q "^# VDSM REVISION 1.3" $MULTIPATH_CONF; then
    :
else
    sed -i '1 s/^/# VDSM REVISION 1.3\n# VDSM PRIVATE\n/' $MULTIPATH_CONF
fi
