import socket
import fcntl
import struct

from autobahn.twisted import wamp
from twisted.internet.task import LoopingCall
from zeroconf import ServiceInfo, Zeroconf

SERVICE_TYPE = '_deskconn._tcp'
SERVICE_PORT = 5020


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('localhost', port)) == 0


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


def initialize_service(ip):
    return ServiceInfo(
        type_="{}.local.".format(SERVICE_TYPE),
        name="{}.{}.local.".format(socket.gethostname(), SERVICE_TYPE),
        address=socket.inet_aton(ip),
        port=SERVICE_PORT,
        properties={"realm": "deskconn"}
    )


class ServiceDiscoveryComponent(wamp.ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self.local_ip = get_local_ip()
        self.service_info = None
        self.zeroconf = Zeroconf()
        self.repeated_called = LoopingCall(self.check_has_ip)
        self.repeated_called.start(5)

    def check_has_ip(self):
        current_ip = get_local_ip()
        if self.local_ip and not current_ip:
            self.stop_publishing()
        elif not self.local_ip and current_ip:
            self.start_publishing()
        elif self.local_ip != current_ip:
            self.start_publishing()
        self.local_ip = current_ip

    def onJoin(self, details):
        self.log.info('session joined: {}'.format(details))
        self.start_publishing()

    def onLeave(self, details):
        self.log.info('session left: {}'.format(details))
        self.repeated_called.stop()
        self.stop_publishing()
        self.disconnect()

    def start_publishing(self):
        if self.service_info:
            self.stop_publishing()
        if not self.local_ip:
            self.log.warn("Not connected to a network...")
            return
        self.service_info = initialize_service(self.local_ip)
        self.log.info("Registering service: {}".format(SERVICE_TYPE))
        self.zeroconf.register_service(self.service_info)
        self.log.info("Registered service: {}".format(SERVICE_TYPE))

    def stop_publishing(self):
        self.log.info("Unregistering service: {}".format(SERVICE_TYPE))
        self.zeroconf.unregister_all_services()
        self.zeroconf.close()
        self.log.info("Unregistered service: {}".format(SERVICE_TYPE))
        self.service_info = None
