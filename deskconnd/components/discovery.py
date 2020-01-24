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
from concurrent.futures import ThreadPoolExecutor
import os
import socket

import zeroconf

from deskconnd.database.controller import is_discovery_enabled

SERVICE_IDENTIFIER = 'deskconn'

ONE_MINUTE = 60
ONE_HOUR = ONE_MINUTE * 60


class Discovery:
    def __init__(self, **kwargs):
        self._desc = kwargs
        self._services = {}
        self.running = False

    def _init_service_info(self, address):
        return zeroconf.ServiceInfo(
            type_=f"_{SERVICE_IDENTIFIER}._tcp.local.",
            name=f"{socket.gethostname()}._{SERVICE_IDENTIFIER}._tcp.local.",
            addresses=[socket.inet_aton(address)],
            port=int(os.environ.get("DESKCONN_PORT", 5020)),
            properties=self._desc,
            host_ttl=ONE_HOUR * 24
        )

    def _init_service(self, address):
        try:
            zconf = zeroconf.Zeroconf([address])
            zconf.register_service(self._init_service_info(address), allow_name_change=False)
            self._services.update({address: zconf})
        except zeroconf.NonUniqueNameException:
            pass

    async def _init_services(self):
        loop = asyncio.get_event_loop()
        futures = []
        executor = ThreadPoolExecutor()
        for address in zeroconf.get_all_addresses():
            futures.append(asyncio.ensure_future(loop.run_in_executor(executor, self._init_service, address)))
        await asyncio.gather(*futures)

    async def _close_services(self):
        if len(self._services) == 0:
            return

        for service in self._services.values():
            service.close()
        self._services.clear()

    async def _sync_services(self):
        while self.running:
            if not await is_discovery_enabled():
                await self._close_services()
                return

            addresses = zeroconf.get_all_addresses()
            # If an interface was gone, unregister the service for that interface
            for address in set(self._services.keys()).difference(addresses):
                self._services.pop(address).close()
            # If a new interface was found, register the service for that
            for address in set(addresses).difference(self._services.keys()):
                self._init_service(address)

            await asyncio.sleep(10)

    async def start(self):
        if self.running:
            return
        self.running = True
        await self._init_services()
        print("Service initialized..")
        # loop.call_later(10, self._sync_services)

    async def stop(self):
        if not self.running:
            return
        self.running = False
        await self._close_services()
