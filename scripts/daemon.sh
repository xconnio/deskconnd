#!/bin/bash

export DESKCONN_PORT=5020
python3 -u "$SNAP"/bin/crossbar start --cbdir "$SNAP_USER_DATA" --config "$SNAP"/.crossbar.yaml
rm -f "$SNAP_COMMON"/state/ready
