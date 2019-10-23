#!/usr/bin/env python3

import argparse

from autobahn.twisted.component import Component, run
from autobahn.wamp.auth import AuthCryptoSign
import pyqrcode

from deskconnd.database.controller import DB


def _print_qr_code(text):
    qr = pyqrcode.create(text, mode='numeric')
    print(qr.terminal(quiet_zone=1))


def generate_otp():
    principle = DB.get_local_principle()
    component = Component(transports="ws://localhost:5020/ws", realm=principle.realm,
                          authentication={"cryptosign": AuthCryptoSign(authid=principle.auth_id,
                                                                       authrole=principle.auth_role,
                                                                       privkey=principle.private_key,
                                                                       authextra={})})

    @component.on_join
    async def joined(session, _details):
        res = await session.call("org.deskconn.deskconnd.pairing.generate")
        _print_qr_code(res)
        print("Scan the QR Code or manually pair with: {}\n".format(res))
        session.leave()

    return component


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
        run([generate_otp()], None)
    elif args.action == 'enable-discovery':
        DB.toggle_discovery(True)
    elif args.action == 'disable-discovery':
        DB.toggle_discovery(False)
    else:
        print("Not yet implemented!")
