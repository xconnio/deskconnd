#!/usr/bin/env python3

from autobahn.twisted.component import Component, run
from autobahn.wamp.auth import AuthCryptoSign
import qrcode

from deskconnd.database.controller import DB


def _print_qr_code(text):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(text)
    qr.print_ascii(tty=True)


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
        print("    Pairing code: {}\n\n".format(res))
        session.leave()

    return component


if __name__ == '__main__':
    run([generate_otp()], None)
