#!/usr/bin/sh

multipath -F
cat <<EOF>> /etc/multipath.conf
blacklist
{
        devnode "*"
}
EOF

systemctl stop multipathd
systemctl disable multipathd
