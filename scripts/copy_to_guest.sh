#!/bin/bash

#
# Usage: copy_to_guest.sh <DISK_NAME> <SOURCE FILE> <DEST ON GUEST DISK>
#


set -e

MOUNT_LOCATION="./mount/"

mkdir -p "$MOUNT_LOCATION"

guestmount -a "$1" -m /dev/sda1 "$MOUNT_LOCATION"

cp "$2" "$MOUNT_LOCATION$3"

chmod +x "$MOUNT_LOCATION$3"

