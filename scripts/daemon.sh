#!/bin/bash

export DESKCONN_PORT=5020

# Ensure the sock directory exists
mkdir -p $SNAP_COMMON/deskconn-sock-dir
export DESKCONN_SOCK_DIR=$SNAP_COMMON/deskconn-sock-dir

python3 -u "$SNAP"/bin/crossbar start --cbdir "$SNAP_USER_DATA" --config "$SNAP"/.crossbar.yaml
