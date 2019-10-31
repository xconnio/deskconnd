#
# Copyright (C) 2019 Omer Akram
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
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

import appdirs

APP_NAME = "deskconnd"
APP_AUTHOR = "org.deskconn"


def is_snap():
    return os.environ.get("SNAP_NAME") in [APP_NAME, 'deskconn', 'piconn']


def get_data_directory():
    if is_snap():
        root = os.path.expandvars('$SNAP_COMMON')
    else:
        root = appdirs.user_state_dir(APP_NAME, APP_AUTHOR)
    return os.path.join(root, 'state')


def get_state_directory():
    state_dir = get_data_directory()
    Path(state_dir).mkdir(parents=True, exist_ok=True)
    return state_dir


READY_PATH = os.path.join(get_state_directory(), 'ready')
