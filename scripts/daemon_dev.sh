#!/bin/bash

export DESKCONN_PORT=5020
export DESKCONN_SOCK_DIR=$HOME
crossbar start --config .crossbar.yaml
