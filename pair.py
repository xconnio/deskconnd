#!/usr/bin/env python3

import os
from pathlib import Path
import tempfile
import uuid

from autobahn.twisted.component import Component, run
from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.internet import reactor


def _is_snap():
    return os.environ.get('SNAP_NAME') == 'deskconnd'


if _is_snap():
    sock_dir = os.path.expandvars('$SNAP_COMMON/deskconnd-sock-dir')
else:
    sock_dir = os.path.expandvars('$HOME/deskconnd-sock-dir')

transport = {
    "type": "rawsocket",
    "url": "ws://localhost/ws",
    "endpoint": UNIXClientEndpoint(reactor, os.path.join(sock_dir, 'deskconnd.sock')),
    "serializer": "cbor",
}

comp = Component(transports=[transport], realm="deskconn")


@comp.on_join
async def joined(session, _details):
    unique_id = str(uuid.uuid4())
    verify_path = os.path.join(tempfile.gettempdir(), unique_id)
    Path(verify_path).touch()
    if os.path.exists(verify_path):
        res = await session.call("org.deskconn.pairing.generate", unique_id)
        print("\nYour Pairing OTP is: {}\n".format(res))
    else:
        print("\nNot able to create {}\n".format(verify_path))
    session.leave()


if __name__ == '__main__':
    run([comp], None)
