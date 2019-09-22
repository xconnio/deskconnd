#!/bin/sh

mkdir -p "$HOME"/deskconnd-sock-dir
export DESKCONND_SOCK_DIR="$HOME"/deskconnd-sock-dir
crossbar start
