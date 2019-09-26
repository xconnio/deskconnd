#!/bin/bash

mkdir -p "$SNAP_COMMON"/crossbar-runtime-dir
mkdir -p "$SNAP_COMMON"/deskconnd-sock-dir
export DESKCONND_SOCK_DIR="$SNAP_COMMON"/deskconnd-sock-dir
crossbar start --cbdir "$SNAP_USER_DATA" --config "$SNAP"/.crossbar/config.yaml
