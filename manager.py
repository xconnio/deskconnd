#!/usr/bin/env python3
#
# Copyright (C) 2018-2020 Omer Akram
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

import asyncio

from autobahn.asyncio.component import run
import txaio
txaio.use_asyncio()  # noqa

from deskconnd.database.controller import init_db
from deskconnd.components.management import main, init_principle, authenticator


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    txaio.config.loop = loop
    loop.run_until_complete(init_db())
    principle = loop.run_until_complete(init_principle())
    run([authenticator(principle), main(principle)])
