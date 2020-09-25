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
import fcntl
import socket
import struct

from twisted.internet.threads import deferToThread
import zeroconf

SERVICE_IDENTIFIER = 'deskconn'

ONE_MINUTE = 60
ONE_HOUR = ONE_MINUTE * 60


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


class Discovery:
    def __init__(self, realm, uid):
        self._desc = {"realm": realm, "uid": uid}
        self._services = {}
        self._looping_call = None
        self.running = False
        self._zeroconf = None

    def _init_service(self):
        address = get_local_ip()
        self._zeroconf = zeroconf.Zeroconf(interfaces=[address])

        service = zeroconf.ServiceInfo(type_=f"_{SERVICE_IDENTIFIER}._tcp.local.",
                                       name=f"{socket.gethostname()}._{SERVICE_IDENTIFIER}._tcp.local.",
                                       port=int(os.environ.get("DESKCONN_PORT")),
                                       addresses=[socket.inet_aton(address)],
                                       properties=self._desc)

        self._zeroconf.register_service(service)

    async def start(self):
        if self.running:
            return

        try:
            await deferToThread(self._init_service)
            self.running = True
        except Exception:
            pass

    def stop(self):
        if self.running:
            deferToThread(self._zeroconf.close)
            self.running = False
