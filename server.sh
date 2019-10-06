#!/bin/bash

SHOULD_PRINT=false

while true
do
  if [ -f "$SNAP_COMMON"/crossbar-runtime-dir/bin/crossbar ]; then
    echo "Crossbar found, now starting..."
    break
  else
    if [ $SHOULD_PRINT = false ]; then
      echo "Waiting for crossbar interface to connect"
      SHOULD_PRINT=true
    fi
    sleep 1
  fi
done

mkdir -p "$SNAP_COMMON"/deskconnd-sock-dir
export DESKCONND_SOCK_DIR="$SNAP_COMMON"/deskconnd-sock-dir
crossbar start --cbdir "$SNAP_USER_DATA" --config "$SNAP"/.crossbar/config.yaml
