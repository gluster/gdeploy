#!/usr/bin/env bash -u
# 
# pass the full path of an unmounted brick as a single argument to unset extended filesystem attributes and 
# erase Gluster FS metadata so that the bick can be added to a different volume
#

brick_path="$1"
setfattr -x trusted.glusterfs.volume-id "$brick_path"
setfattr -x trusted.gfid "$brick_path"
rm -rf "$brick_path/.glusterfs"
