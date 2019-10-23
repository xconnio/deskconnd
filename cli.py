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

from deskconnd.database.controller import DB


def _print_qr_code(text):
    import pyqrcode

    qr = pyqrcode.create(text, mode='numeric')
    print(qr.terminal(quiet_zone=1))


def generate_otp():
    from autobahn.twisted.component import Component, run
    from autobahn.wamp.auth import AuthCryptoSign

    principle = DB.get_local_principle()
    component = Component(transports="ws://localhost:5020/ws", realm=principle.realm,
                          authentication={"cryptosign": AuthCryptoSign(authid=principle.auth_id,
                                                                       authrole=principle.auth_role,
                                                                       privkey=principle.private_key,
                                                                       authextra={})})

    @component.on_join
    async def joined(session, _details):
        res = await session.call("org.deskconn.deskconnd.pair")
        _print_qr_code(res)
        print("Scan the QR Code or manually pair with: {}\n".format(res))
        session.leave()

    run([component], None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DeskConn command line utility')
    parser.add_argument('action',
                        metavar='ACTION',
                        type=str,
                        help='DeskConn CLI interface, accepts any of these: pair, enable-discovery, '
                             'disable-discovery',
                        choices=['pair', 'enable-discovery', 'disable-discovery'])

    args = parser.parse_args()
    if args.action == 'pair':
        generate_otp()
    elif args.action == 'enable-discovery':
        DB.toggle_discovery(True)
    elif args.action == 'disable-discovery':
        DB.toggle_discovery(False)
    else:
        print("Not yet implemented!")
