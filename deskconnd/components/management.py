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

from autobahn.wamp.auth import AuthCryptoSign, AuthAnonymous
from autobahn.asyncio.component import Component
from autobahn.wamp.cryptobox import KeyRing
from pathlib import Path
import txaio
txaio.use_asyncio()  # noqa

from deskconnd.database.controller import refresh_local_principle, is_discovery_enabled, toggle_discovery
from deskconnd.components.authentication import Authentication
from deskconnd.components.discovery import Discovery
from deskconnd.environment import READY_PATH

REALM = 'deskconn'


async def init_principle():
    return await refresh_local_principle(KeyRing().generate_key_hex(), REALM, REALM)


def authenticator(principle):
    component = Component(transports="ws://localhost:5020/ws", realm=principle.realm,
                          authentication={"anonymous": AuthAnonymous(auth_role="authenticator")})

    @component.on_join
    async def joined(session, _details):
        auth = Authentication(principle)
        await session.register(auth.authenticate, 'org.deskconn.deskconnd.authenticate')
        await session.register(auth.generate_otp, 'org.deskconn.deskconnd.pair')

    return component


def main(principle):
    component = Component(transports="ws://localhost:5020/ws", realm=principle.realm,
                          authentication={"cryptosign": AuthCryptoSign(authid=principle.auth_id,
                                                                       authrole=principle.auth_role,
                                                                       privkey=principle.private_key)})

    @component.on_join
    async def joined(session, _details):
        discovery = Discovery()
        if await is_discovery_enabled():
            await toggle_discovery(True)

        async def enable_discovery():
            await toggle_discovery(True)
            await discovery.start()

        async def disable_discovery():
            await toggle_discovery(False)
            await discovery.stop()

        await session.register(enable_discovery, 'org.deskconn.deskconnd.discovery.enable')
        await session.register(disable_discovery, 'org.deskconn.deskconnd.discovery.disable')

        Path(READY_PATH).touch()

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
    async def _enable_discovery(self):
        DB.toggle_discovery(True)
        await self._discovery.start()

    async def _disable_discovery(self):
        DB.toggle_discovery(False)
        await self._discovery.stop()
