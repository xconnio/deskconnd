#
# Copyright (C) 2020 Omer Akram
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
from autobahn.wamp.cryptosign import SigningKey
from nacl.public import PrivateKey
from nacl.encoding import HexEncoder


# This example shows illustrates public key "pairing" with deskconnd


def main(_aioloop, _session):
    print("Successfully paired with server\n")
    print("Public key: {}".format(public_key_hex))
    print("Private key: {}\n".format(private_key_hex))
    print("For practical use, you may need to store the key pair storage for reuse")


if __name__ == '__main__':
    parser = argparse.ArgumentParser("DeskConnD pairing")
    parser.add_argument("otp", type=int)
    args = parser.parse_args()

    key = PrivateKey.generate()
    signing_key = SigningKey.from_key_bytes(key.encode())
    public_key_hex = signing_key.public_key()
    private_key_hex = key.encode(HexEncoder).decode('ascii')

    auth = AuthCryptoSign(authrole="deskconn", authid=public_key_hex, privkey=private_key_hex,
                          authextra={"otp": args.otp})
    component = Component(main=main, transports="ws://localhost:5020/ws", realm="deskconn",
                          authentication={"cryptosign": auth})
    run(component, log_level='warn')
