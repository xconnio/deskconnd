import os
import socket

from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import zeroconf

from deskconnd.database.controller import DB

SERVICE_IDENTIFIER = 'deskconn'


class Discovery:
    def __init__(self, realm, uid):
        self._desc = {"realm": realm, "uid": uid}
        self._services = {}
        self._looping_call = None

    def _init_service_info(self, address):
        return zeroconf.ServiceInfo(
            type_=f"_{SERVICE_IDENTIFIER}._tcp.local.",
            name=f"{socket.gethostname()}._{SERVICE_IDENTIFIER}._tcp.local.",
            addresses=[socket.inet_aton(address)],
            port=int(os.environ.get("DESKCONN_PORT")),
            properties=self._desc
        )

    def _init_service(self, address):
        zconf = zeroconf.Zeroconf([address])
        zconf.register_service(self._init_service_info(address), 10, True)
        self._services.update({address: zconf})

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
        self._looping_call = LoopingCall(self._sync_services)
        self._looping_call.start(10, False)
        reactor.callInThread(self._init_services)

    def stop(self):
        self._looping_call.stop()
        self._close_services()
