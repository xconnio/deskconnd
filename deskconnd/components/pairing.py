import os
import pickle
import random
from pathlib import Path
import tempfile

from autobahn import wamp
from autobahn.wamp import ApplicationError
from autobahn.wamp.cryptobox import KeyRing
from autobahn.twisted.wamp import ApplicationSession
from sqlitedict import SqliteDict
import txaio


def add_key(key_authid, realm, role):
    db_path = os.path.join(os.environ.get("HOME"), "deskconn.sqlite")
    db = SqliteDict(db_path)
    db[key_authid] = {'pubkey': key_authid, 'realm': realm, 'role': role}
    db.commit()
    db.close()


def get_principal(key):
    db_path = os.path.join(os.environ.get("HOME"), "deskconn.sqlite")
    db = SqliteDict(db_path)
    for k, v in db.items():
        if k == key:
            return v
    return {}


class PairingComponent(ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self._pending_otps = []
        self._key_file = os.path.join(os.environ.get("HOME"), "deskconn.keys")
        self._public_key = None
        self._private_key = None
        self._generate_and_save_key_pair()

    def _generate_and_save_key_pair(self):
        if os.path.exists(self._key_file):
            with open(self._key_file, 'rb') as file:
                self._private_key, self._public_key = pickle.load(file)
        else:
            self._private_key, self._public_key = KeyRing().generate_key_hex()
            with open(self._key_file, 'wb') as file:
                pickle.dump((self._private_key, self._public_key), file)

    async def onJoin(self, details):
        self.log.info('realm joined: {}'.format(details.realm))
        await self.register(self, prefix="org.deskconn.deskconnd.pairing.")

    def _revoke_key(self, key):
        if key in self._pending_otps:
            self._pending_otps.remove(key)

    @wamp.register(None)
    async def generate(self, local_identity_token):
        token_path = os.path.join(tempfile.gettempdir(), local_identity_token)
        if os.path.exists(token_path):
            Path(token_path).unlink()
            key = random.randint(100000, 999999)
            self._pending_otps.append(key)
            txaio.call_later(30, self._revoke_key, key)
            return key
        raise wamp.ApplicationError("org.deskconn.deskconnd.errors.invalid_caller")

    @wamp.register(None)
    async def pair(self, otp, public_key):
        assert otp.isdigit()
        otp = int(otp.strip())
        if otp in self._pending_otps:
            self._pending_otps.remove(otp)
            add_key(public_key, 'deskconn', 'deskconn')
            return True
        raise wamp.ApplicationError("org.deskconn.deskconnd.errors.invalid_otp")


class AuthenticatorSession(ApplicationSession):
    async def onJoin(self, details):
        def authenticate(_realm, authid, auth_details):
            assert ('authmethod' in auth_details)
            assert (auth_details['authmethod'] == 'cryptosign')
            self.log.info("authenticating session with public key = {pubkey}", pubkey=authid)
            principal = get_principal(authid)
            if principal:
                return {
                    'pubkey': authid,
                    'realm': principal['realm'],
                    'authid': authid,
                    'role': principal['role'],
                    'cache': True
                }
            else:
                raise ApplicationError('org.deskconn.deskconnd.no_such_user',
                                       'no principal with matching public')

        await self.register(authenticate, 'org.deskconn.deskconnd.authenticate')
