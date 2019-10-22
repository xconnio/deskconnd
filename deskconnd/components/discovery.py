import fcntl
import os
import socket
import struct
import time

from autobahn.twisted import wamp
from twisted.internet.task import LoopingCall
from zeroconf import ServiceInfo, Zeroconf

SERVICE_TYPE = '_deskconn._tcp'
FALLBACK_PORT = 5020


def get_ip_address(iface):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packed_ip = fcntl.ioctl(sock.fileno(), 0x8915, struct.pack('256s', iface[:15]))[20:24]
    return socket.inet_ntoa(packed_ip)


def get_default_gateway_linux():
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue
            return fields[0]
    return None


def get_local_ip():
    gateway = get_default_gateway_linux()
    if gateway:
        return get_ip_address(bytes(gateway, 'utf-8'))
    return gateway


def get_system_uid():
    with open("/etc/machine-id") as file:
        return file.read().strip()


def initialize_service(ip):
    return ServiceInfo(
        type_="{}.local.".format(SERVICE_TYPE),
        name="{}.{}.local.".format(socket.gethostname(), SERVICE_TYPE),
        address=socket.inet_aton(ip),
        port=os.environ.get("$DESKCONN_PORT", FALLBACK_PORT),
        properties={"realm": "deskconn", "uid": get_system_uid()}
    )


class ServiceDiscoverySession(wamp.ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self.running = False
        self.local_ip = None
        self.zeroconf = Zeroconf()
        self.repeated_call = None
        self.unregister_on_connect = False

    def check_has_ip(self):
        current_ip = get_local_ip()
        if self.running and not current_ip:
            self.unregister_on_connect = True
            self.local_ip = None
            return

        if self.unregister_on_connect:
            self.stop_publishing(True)
            self.unregister_on_connect = False

        if self.local_ip and not current_ip:
            self.stop_publishing()
            self.local_ip = current_ip
        elif not self.local_ip and current_ip:
            self.local_ip = current_ip
            self.start_publishing()
        elif self.local_ip != current_ip:
            self.local_ip = current_ip
            self.start_publishing()

    async def onJoin(self, details):
        self.log.info('session joined: {}'.format(details))
        self.repeated_call = LoopingCall(self.check_has_ip)
        self.repeated_call.start(5)
        self.check_has_ip()

    def onLeave(self, details):
        self.log.info('session left: {}'.format(details))
        self.repeated_call.stop()
        self.stop_publishing()
        self.zeroconf.close()
        self.disconnect()

    def start_publishing(self):
        if self.running:
            self.stop_publishing()
        self.log.info("Registering service: {}".format(SERVICE_TYPE))
        self.zeroconf.register_service(initialize_service(self.local_ip))
        self.log.info("Registered service: {}".format(SERVICE_TYPE))
        self.running = True

    def stop_publishing(self, wait=False):
        self.zeroconf.close()
        if wait:
            time.sleep(1)
        self.running = False
        self.log.info("Unregistered service: {}".format(SERVICE_TYPE))
