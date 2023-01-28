#!/bin/bash

set -e

MOUNT_LOCATION="./mount/"

fusermount -u "$MOUNT_LOCATION"

rmdir "$MOUNT_LOCATION"