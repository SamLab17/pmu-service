#!/bin/bash

#
# Usage: remove_guest_file.sh <DISK_NAME> <DEST ON GUEST DISK>
#


set -e

MOUNT_LOCATION="./mount/"

mkdir -p "$MOUNT_LOCATION"

guestmount -a "$1" -m /dev/sda1 "$MOUNT_LOCATION"

rm -f "$MOUNT_LOCATION$2"

