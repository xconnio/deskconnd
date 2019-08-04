#!/usr/bin/python3
#
# Copyright (C) 2018-2019  Omer Akram
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

import os
from pathlib import Path

from crossbar import run


def _is_snap():
    return os.environ.get('SNAP_NAME') == 'deskconnd'


def get_start_params():
    params = ['start']
    if _is_snap():
        params.append('--cbdir')
        params.append(os.environ.get('SNAP_USER_DATA'))
        params.append('--config')
        params.append(os.path.join(os.environ.get('SNAP'), '.crossbar/config.yaml'))
        Path(os.path.expandvars('$SNAP_COMMON/avahi-services-dir')).mkdir(exist_ok=True)
        sock_dir = os.path.expandvars('$SNAP_COMMON/deskconnd-sock-dir')
    else:
        sock_dir = os.path.expandvars('$HOME/deskconnd-sock-dir')

    Path(sock_dir).mkdir(exist_ok=True)
    os.environ['DESKCONND_SOCK_DIR'] = sock_dir
    return params


def main():
    run(get_start_params())


if __name__ == '__main__':
    main()
