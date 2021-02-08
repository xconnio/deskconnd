#!/usr/bin/env python3
#
# Copyright (C) 2019 Omer Akram
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

import argparse
import sys

from autobahn.twisted.component import Component, run
from autobahn.wamp.auth import AuthCryptoSign
import pyqrcode

from deskconnd.database.controller import DB

principle = DB().get_local_principle()
if principle is None:
    print("The backend is likely not running, please ensure its up.")
    sys.exit(1)

authid = principle.authid
authrole = principle.authrole
privkey = principle.privkey
realm = principle.realm


component = Component(transports="ws://127.0.0.1:5020/ws", realm=realm,
                      authentication={"cryptosign": AuthCryptoSign(authid=authid, authrole=authrole, privkey=privkey)})


@component.on_connectfailure
def fail(_component: Component, message):
    print("Unable to connect to backend. Please ensure it's running.")
    _component.stop()


def _print_qr_code(text):
    qr = pyqrcode.create(text, mode='numeric')
    print(qr.terminal(quiet_zone=1))


def generate_otp():
    @component.on_join
    async def joined(session, _details):
        res = await session.call("org.deskconn.generate_otp")
        _print_qr_code(res)
        print("Scan the QR Code or manually pair with: {}\n".format(res))
        print(authid, authrole, privkey)
        session.leave()

    run([component], None)


def toggle_discovery(enable):
    @component.on_join
    async def joined(session, _details):
        if enable:
            procedure = "org.deskconn.enable_discovery"
        else:
            procedure = "org.deskconn.disable_discovery"

        await session.call(procedure)
        session.leave()

    run([component], None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DeskConn command line utility')
    commands = parser.add_subparsers(title='Available commands', dest='command')
    discovery = commands.add_parser("discovery")
    discovery.add_argument('status', type=str, choices=('enable', 'disable'))
    commands.add_parser('pair')
    args = parser.parse_args()

    if args.command == 'pair':
        generate_otp()
    elif args.command == 'discovery':
        if args.status == 'enable':
            toggle_discovery(True)
        else:
            toggle_discovery(False)
    else:
        parser.print_help()
