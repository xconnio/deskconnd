#!/usr/bin/env python3
#
# Copyright (C) 2019-2020 Omer Akram
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
import argparse
import sys

from autobahn.asyncio.component import Component, run
from autobahn.wamp.auth import AuthCryptoSign
import qrcode
import txaio
txaio.use_asyncio()  # noqa

from deskconnd.database.controller import get_local_principle, init_db, close_db


def _print_qr_code(text):
    qr = qrcode.QRCode()
    qr.add_data(text)
    qr.print_tty()


async def construct_connection(main):
    principle = await get_local_principle()
    if not principle:
        print("The backend is likely not running, please ensure its up.")
        sys.exit(1)
    return Component(transports="ws://localhost:5020/ws", realm=principle.realm, main=main,
                     authentication={"cryptosign": AuthCryptoSign(authid=principle.auth_id,
                                                                  authrole=principle.auth_role,
                                                                  privkey=principle.private_key)})


async def generate_otp(reactor, session):
    print(reactor, session)
    res = await session.call("org.deskconn.deskconnd.pair")
    _print_qr_code(res)
    print("\nScan the QR Code or manually pair with: {}\n".format(res))


async def toggle_discovery(reactor, session):
    if args.status == 'enable':
        procedure = "org.deskconn.deskconnd.discovery.enable"
    else:
        procedure = "org.deskconn.deskconnd.discovery.disable"

    await session.call(procedure)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DeskConn command line utility')
    commands = parser.add_subparsers(title='Available commands', dest='command')
    discovery = commands.add_parser("discovery")
    discovery.add_argument('status', type=str, choices=('enable', 'disable'))
    commands.add_parser('pair')
    args = parser.parse_args()

    if args.command != 'pair' and args.command != 'discovery':
        parser.print_help()
        sys.exit(0)

    loop = asyncio.get_event_loop()
    txaio.config.loop = loop
    loop.run_until_complete(init_db())

    if args.command == 'pair':
        component = loop.run_until_complete(construct_connection(generate_otp))
        loop.run_until_complete(close_db())
        run(component, log_level='warn')
    elif args.command == 'discovery':
        component = loop.run_until_complete(construct_connection(toggle_discovery))
        loop.run_until_complete(close_db())
        run(component, log_level='warn')
