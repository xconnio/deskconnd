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

from autobahn.asyncio.component import Component, run
from autobahn.wamp.auth import AuthCryptoSign
import qrcode

from deskconnd.database.controller import DB

principle = DB.get_local_principle()
if not principle:
    print("The backend is likely not running, please ensure its up.")
    sys.exit(1)
component = Component(transports="ws://localhost:5020/ws", realm=principle.realm,
                      authentication={"cryptosign": AuthCryptoSign(authid=principle.auth_id,
                                                                   authrole=principle.auth_role,
                                                                   privkey=principle.private_key)})


def _print_qr_code(text):
    qr = qrcode.QRCode()
    qr.add_data(text)
    qr.print_tty()


def generate_otp():
    @component.on_join
    async def joined(session, _details):
        res = await session.call("org.deskconn.deskconnd.pair")
        _print_qr_code(res)
        print("\nScan the QR Code or manually pair with: {}\n".format(res))
        session.leave()

    run(component, log_level='warn')


def toggle_discovery(enabled):
    @component.on_join
    async def joined(session, _details):
        if enabled:
            procedure = "org.deskconn.deskconnd.discovery.enable"
        else:
            procedure = "org.deskconn.deskconnd.discovery.disable"

        await session.call(procedure)
        session.leave()

    run(component, log_level='warn')


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
