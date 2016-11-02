#!/bin/bash
brick_path=$1
setfattr -x trusted.glusterfs.volume-id $brick_path
setfattr -x trusted.gfid $brick_path
rm -rf $brick_path/.glusterfs
