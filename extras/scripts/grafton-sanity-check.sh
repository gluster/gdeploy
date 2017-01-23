#!/usr/bin/bash

# This script was initially written to solve the bug:
# https://bugzilla.redhat.com/show_bug.cgi?id=1405447
#
# Comment #1:
# 1. Disks ( RAID volumes ) should be blank and should not contain any
# partition table. If there are MBR/GPT partition style information available,
# gdeploy should throw proper warning and stop proceeding

# 2. Network configuration.
# The hostname of the server should resolve to the same IP address on all
# the servers.

DATE=`date '+%Y_%m_%d'`
PATTERN=host_ip_${DATE}.txt
FILE=/tmp/`hostname`_$PATTERN

cleanup ()
{
    # Clean up after the work is done
    /bin/rm /tmp/*_${PATTERN}
}

host_resolvability_check ()
{
    # Check if the given hostnames resolve to same ip address on all the
    # machines.
    # Use ping to get the ip address (don't bother with `dig +short' or `host'
    # and other friends. If the hostsnames are configured in /etc/hosts the
    # above commands fail. ping is reliable source for now.

    # Cleanup any existing data
    :> $FILE

    # Choose one of the nodes as master
    MASTER=`echo $1 | cut -d, -f1`
    for hostname in `echo $1 | tr ',' ' '`; do
        # Get the ip address for the hostname, if ping fails we exit
        # immediately. The given hostname is not pingable
        ip=`ping -c1 -q $hostname | awk '/PING/ { print $3}' |
                 sed -e 's/(//' -e 's/)//'`

        if [ -z $ip ]; then
            echo "ping failed unable to reach $hostname"
        fi

        if [ "X$hostname" = "X$MASTER" ]; then
            MASTERIP=$ip
        fi

        cat <<EOF>>${FILE}
$hostname $ip
EOF
    done

    # Sort the contents of the file
    sort ${FILE} -o ${FILE}

    # Copy all the files to MASTER and compare
    match=0
    if ifconfig | egrep -q $MASTERIP; then
        # Give some time for the operation to finish on other nodes
        sleep 2
        for node in `echo $1 | tr ',' ' '`; do
            if [ "$node" = "$MASTER" ]; then
                continue
            fi
            ip=`ping -c1 -q $node | awk '/PING/ { print $3}' |
                     sed -e 's/(//' -e 's/)//'`
            scp $ip:/tmp/*_${PATTERN} /tmp/
        done
        # Compare the files
        for file in /tmp/*_${PATTERN}; do
            if ! diff -q $FILE $file; then
                match=1
                echo "ip address and hostname does not match"
            fi
        done
        if [ $match -eq 1 ]; then
            exit 2
        fi
    fi
    # In case of successful run, clean up the files
    # We leave behind the files for the user to examine the errors
    cleanup
}

partition_table_check ()
{
    # Check the partition table, if GPT exit with non zero status
    for disk in `echo $1 | tr ',' ' '`; do
        # Handle absolute paths as well
        if fdisk -l /dev/`basename $disk` 2>/dev/null | \
               grep 'Disk label.*gpt$' ; then
            echo "Disk $disk contains GPT disk label, exiting!"
            exit 2
        fi
    done
}

main ()
{
    if [ $# -eq 0 ]; then
        echo "Usage: $0 -d disks -h hosts"
    fi

    # Values to option -d should be like: -d vda,vdb or -d "vda vdb"
    while getopts "d:h:" opt; do
        case $opt in
            d)
                disks="$OPTARG"
                partition_table_check "$disks"
                ;;
            h)
                hosts="$OPTARG"
                host_resolvability_check $hosts
                ;;
        esac
    done
    shift $((OPTIND-1))
}

main "$@"
