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
import os
from pathlib import Path

from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp.auth import AuthCryptoSign
from autobahn.asyncio.component import Component, run
from autobahn.wamp.cryptobox import KeyRing
import txaio
txaio.use_asyncio()  # noqa

from deskconnd.database.controller import DB
# from deskconnd.components._discovery import Discovery
from deskconnd.components._authentication import Authentication
# from deskconnd.environment import READY_PATH

REALM = 'deskconn'


async def init_principle():
    return await DB.refresh_local_principle(KeyRing().generate_key_hex(), REALM, REALM)


def main(principle):
    component = Component(transports="ws://localhost:5020/ws", realm=principle.realm,
                          authentication={"cryptosign": AuthCryptoSign(authid=principle.auth_id,
                                                                       authrole=principle.auth_role,
                                                                       privkey=principle.private_key)})

    @component.on_join
    async def joined(session, details):
        auth = Authentication(principle)
        await session.register(auth.authenticate, 'org.deskconn.deskconnd.authenticate')
        await session.register(auth.generate_otp, 'org.deskconn.deskconnd.pair')
        # await session.register(self._enable_discovery, 'org.deskconn.deskconnd.discovery.enable')
        # await session.register(self._disable_discovery, 'org.deskconn.deskconnd.discovery.disable')

    return component

#
# class ManagementSession(ApplicationSession):
#     def __init__(self, config=None):
#         super().__init__(config)
#         self._system_uid = DB.init_config()
#         self._principle = DB.refresh_local_principle(KeyRing().generate_key_hex(), config.realm, config.realm)
#         self._discovery = Discovery(realm=config.realm, uuid=self._system_uid)
#         if DB.is_discovery_enabled():
#             self._discovery.start()
#         self._auth = Authentication(self._principle)
#
#     def onConnect(self):
#         self.join(self._principle.realm, ['cryptosign'], self._principle.auth_id, self._principle.auth_role)
#
#     async def onJoin(self, details):
#         self.log.info('realm joined: {}'.format(details.realm))
#         Path(READY_PATH).touch()
#
#     def onLeave(self, details):
#         if os.path.exists(READY_PATH):
#             Path(READY_PATH).unlink()
#         self._discovery.stop()
#         self.disconnect()
#
#     async def _enable_discovery(self):
#         DB.toggle_discovery(True)
#         await self._discovery.start()
#
#     async def _disable_discovery(self):
#         DB.toggle_discovery(False)
#         await self._discovery.stop()
