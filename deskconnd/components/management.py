#
# Copyright (C) 2018-2019 Omer Akram
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

from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.cryptobox import KeyRing

from deskconnd.database.controller import DB
from deskconnd.components._discovery import Discovery
from deskconnd.components._authentication import Authentication

from deskconnd.environment import get_state_directory


class ManagementSession(ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self._system_uid = DB.init_config()
        self._principle = DB.refresh_local_principle(KeyRing().generate_key_hex(), config.realm, config.realm)
        self._discovery = Discovery(config.realm, self._system_uid)
        if DB.is_discovery_enabled():
            self._discovery.start()
        self._auth = Authentication(self._principle)

    def onConnect(self):
        self.join(self._principle.realm, ['cryptosign'], self._principle.auth_id, self._principle.auth_role)

    async def onJoin(self, details):
        self.log.info('realm joined: {}'.format(details.realm))
        await self.register(self._auth.authenticate, 'org.deskconn.deskconnd.authenticate')
        await self.register(self._auth.generate_otp, 'org.deskconn.deskconnd.pair')
        await self.register(self._enable_discovery, 'org.deskconn.deskconnd.discovery.enable')
        await self.register(self._disable_discovery, 'org.deskconn.deskconnd.discovery.disable')
        self.on_started()

    def onLeave(self, details):
        self.on_stopped()
        self._discovery.stop()
        self.disconnect()

    async def _enable_discovery(self):
        DB.toggle_discovery(True)
        self._discovery.start()

    async def _disable_discovery(self):
        DB.toggle_discovery(False)
        self._discovery.stop()

    @staticmethod
    def on_started():
        Path(os.path.join(get_state_directory(), 'ready')).touch()

    @staticmethod
    def on_stopped():
        directory = get_state_directory()
        ready_file = os.path.join(directory, 'ready')
        if os.path.exists(directory) and os.path.exists(ready_file):
            Path(ready_file).unlink()
