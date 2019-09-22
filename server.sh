#!/bin/bash

mkdir -p "$SNAP_COMMON"/avahi-services-dir
mkdir -p "$SNAP_COMMON"/deskconnd-sock-dir
export DESKCONND_SOCK_DIR="$SNAP_COMMON"/deskconnd-sock-dir
crossbar start --cbdir "$SNAP_USER_DATA" --config "$SNAP"/.crossbar/config.yaml
