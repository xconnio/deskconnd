import os
import socket

from autobahn.twisted import wamp
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import zeroconf

SERVICE_IDENTIFIER = 'deskconn'


class ServiceDiscoverySession(wamp.ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self.services = {}
        self.looping_call = None

    @classmethod
    def get_system_uid(cls):
        with open("/etc/machine-id") as file:
            return file.read().strip()

    def initialize_service_info(self, address):
        return zeroconf.ServiceInfo(
            type_=f"_{SERVICE_IDENTIFIER}._tcp.local.",
            name=f"{socket.gethostname()}._{SERVICE_IDENTIFIER}._tcp.local.",
            addresses=[socket.inet_aton(address)],
            port=int(os.environ.get("DESKCONN_PORT")),
            properties={"realm": "deskconn", "uid": self.get_system_uid()}
        )

    def initialize_service(self, address):
        zconf = zeroconf.Zeroconf([address])
        zconf.register_service(self.initialize_service_info(address), 20, True)
        self.services.update({address: zconf})

    def initialize_services(self):
        for address in zeroconf.get_all_addresses():
            self.initialize_service(address)

    def close_services(self):
        for service in self.services.values():
            reactor.callInThread(service.close)
        self.services.clear()

    async def onJoin(self, details):
        self.log.info('session joined: {}'.format(details))
        reactor.callInThread(self.initialize_services)
        self.looping_call = LoopingCall(self.sync_services)
        self.looping_call.start(5, False)

    def onLeave(self, details):
        self.log.info('session left: {}'.format(details))
        self.close_services()

    def sync_services(self):
        addresses = zeroconf.get_all_addresses()
        to_unregister = [address for address in self.services.keys() if address not in addresses]
        to_register = [address for address in addresses if address not in self.services.keys()]

        def _sync():
            for address in to_unregister:
                self.services.pop(address).close()
            for address in to_register:
                self.initialize_service(address)

        reactor.callInThread(_sync)
