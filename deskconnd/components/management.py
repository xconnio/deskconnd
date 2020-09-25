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

from autobahn.wamp import register
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.cryptobox import KeyRing

from deskconnd.database.controller import DB
from deskconnd.components._discovery import Discovery
from deskconnd.components._authentication import Authentication


class ManagementSession(ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self.db = DB()
        self._system_uid = self.db.init_config()
        self._principle = self.db.refresh_local_principle(KeyRing().generate_key_hex(), config.realm, config.realm)
        self._discovery = Discovery(config.realm, self._system_uid)
        self._auth = Authentication(self._principle)

    def onConnect(self):
        self.join(self._principle.realm, ['cryptosign'], self._principle.authid, self._principle.authrole)

    async def onJoin(self, details):

        regs = await self.register(self._auth, prefix='org.deskconn.')
        for reg in regs:
            self.log.info(f"Registered procedure {reg.procedure}")

        regs = await self.register(self, prefix='org.deskconn.')
        for reg in regs:
            self.log.info(f"Registered procedure {reg.procedure}")

        await self.enable_discovery()

        if self.db.is_discovery_enabled():
            await self._discovery.start()

    def onLeave(self, details):
        self._discovery.stop()

    @register(None)
    async def enable_discovery(self):
        self.db.toggle_discovery(True)
        await self._discovery.start()

    @register(None)
    def disable_discovery(self):
        self.db.toggle_discovery(False)
        self._discovery.stop()
