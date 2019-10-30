#!/bin/bash

SHOULD_PRINT=true

while true
do
  if [ -f "$SNAP_COMMON"/crossbar-runtime-dir/crossbar/bin/crossbar ]; then
    echo "Crossbar found, now starting..."
    break
  else
    if [ $SHOULD_PRINT = true ]; then
      echo "Waiting for crossbar runtime directory interface to connect"
      SHOULD_PRINT=false
    fi
    sleep 1
  fi
done

export DESKCONN_PORT=5020
python3.8 -u "$(which crossbar)" start --cbdir "$SNAP_USER_DATA" --config "$SNAP"/.crossbar.yaml
