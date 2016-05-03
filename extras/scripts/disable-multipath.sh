#!/usr/bin/sh

cat <<EOF>> /etc/multipath.conf
blacklist
{
        devnode "*"
}
EOF

systemctl stop multipathd
systemctl disable multipathd
