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
import signal
import functools
import os
from pathlib import Path

from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp.auth import AuthCryptoSign
from autobahn.asyncio.component import Component, run
from autobahn.wamp.cryptobox import KeyRing
from tortoise import Tortoise
import txaio
txaio.use_asyncio()  # noqa

from deskconnd.database.controller import DB
from deskconnd.components.management import main, init_principle
# from deskconnd.components._discovery import Discovery
# from deskconnd.components._authentication import Authentication
# from deskconnd.environment import READY_PATH


async def on_interrupt():
    await Tortoise.close_connections()
    loop.stop()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    txaio.config.loop = loop

    loop.run_until_complete(DB.init_db())
    loop.add_signal_handler(signal.SIGINT, functools.partial(asyncio.ensure_future, on_interrupt()))
    loop.add_signal_handler(signal.SIGTERM, functools.partial(asyncio.ensure_future, on_interrupt()))

    principle = loop.run_until_complete(init_principle())
    run(main(principle))
