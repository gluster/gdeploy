#!/usr/bin/env bash

# This script is not intended to be run by the user. It will be called by
# gdeploy.
NODE=$1
NEW_NODE=$2
VOLUMENAME=$3
VOLDIR="/var/lib/glusterd/vols/$VOLUMENAME"

# Test if passwordless ssh is setup to the node that has to be replaced.
ssh -oBatchMode=yes root@$NEW_NODE date > /dev/null
test $? -ne 0 && {
    echo "Passwordless ssh is not set to $NEW_NODE exiting..."
    exit 1
}

# Get the UUID of the node that has to be replaced
UUID=`gluster peer status | grep -A2 $NEW_NODE| awk '/Uuid/ {print $2}'`

# UUID of the healthy node, so that we can build the peerinfo
HOSTUUID=`awk -F= '/UUID/ {print $2}' /var/lib/glusterd/glusterd.info`

# The brick to create
BRICK=`gluster vol info $VOLUMENAME | grep $NEW_NODE | cut -d: -f3`

# Host brick, to get the volume-id
HOSTBRICK=`gluster vol info $VOLUMENAME | grep $NODE | cut -d: -f3`
VOLUME_ID=`getfattr -d -ehex -m. $HOSTBRICK 2>/dev/null | \
awk -F= '/volume-id/ {print $2}'`

# Clean up /var/tmp/peers - We don't need stray data
rm -rf /var/tmp/peers

cp -r /var/lib/glusterd/peers /var/tmp/
rm -f /var/tmp/peers/$UUID      # remove the failed UUID

cat <<EOF>/var/tmp/replace_uuid.sh
#!/usr/bin/env bash

sed -i "s/\(UUID=\).*/\1$UUID/" /var/lib/glusterd/glusterd.info

# Create backend directory
mkdir -p $BRICK

# Build peer info of the node
cat <<EOF1 > /var/lib/glusterd/peers/$HOSTUUID
UUID=$HOSTUUID
state=3
hostname=$NODE
EOF1

# Set the volume-id attribute
setfattr -n trusted.glusterfs.volume-id -v $VOLUME_ID $BRICK

EOF

# Copy the files to the new node
scp -r /var/tmp/peers root@$NEW_NODE:/var/lib/glusterd/ >/dev/null 2>&1
scp -r /var/tmp/replace_uuid.sh root@$NEW_NODE:/var/tmp/ >/dev/null 2>&1
ssh root@$NEW_NODE chmod 755 /var/tmp/replace_uuid.sh
