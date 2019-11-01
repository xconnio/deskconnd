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
import socket

from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import zeroconf

from deskconnd.database.controller import DB

SERVICE_IDENTIFIER = 'deskconn'

ONE_MINUTE = 60
ONE_HOUR = ONE_MINUTE * 60


class Discovery:
    def __init__(self, realm, uid):
        self._desc = {"realm": realm, "uid": uid}
        self._services = {}
        self._looping_call = None
        self.running = False

    def _init_service_info(self, address):
        return zeroconf.ServiceInfo(
            type_=f"_{SERVICE_IDENTIFIER}._tcp.local.",
            name=f"{socket.gethostname()}._{SERVICE_IDENTIFIER}._tcp.local.",
            addresses=[socket.inet_aton(address)],
            port=int(os.environ.get("DESKCONN_PORT")),
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

    def _init_services(self):
        for address in zeroconf.get_all_addresses():
            self._init_service(address)

    def _close_services(self):
        if len(self._services) == 0:
            return

        for service in self._services.values():
            reactor.callInThread(service.close)
        self._services.clear()

    def _sync_services(self):
        if not DB.is_discovery_enabled():
            self._close_services()
            return

        addresses = zeroconf.get_all_addresses()
        to_unregister = [address for address in self._services.keys() if address not in addresses]
        to_register = [address for address in addresses if address not in self._services.keys()]

        def sync():
            for address in to_unregister:
                self._services.pop(address).close()
            for address in to_register:
                self._init_service(address)

        reactor.callInThread(sync)

    def start(self):
        if self.running:
            return
        self.running = True
        self._looping_call = LoopingCall(self._sync_services)
        self._looping_call.start(10, False)
        reactor.callInThread(self._init_services)

    def stop(self):
        if not self.running:
            return
        self._looping_call.stop()
        self._close_services()
        self.running = False
