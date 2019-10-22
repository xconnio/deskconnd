import random

from autobahn.wamp import ApplicationError
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.cryptobox import KeyRing
import txaio

from deskconnd.database.controller import DB


class AuthSession(ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self._pending_otps = []
        self._principle = DB.refresh_local_principle(KeyRing().generate_key_hex(), config.realm, config.realm)

    def onConnect(self):
        self.join(self._principle.realm, ["cryptosign"], self._principle.auth_id, self._principle.auth_role)

    async def onJoin(self, details):
        self.log.info('realm joined: {}'.format(details.realm))
        await self.register(self._generate, "org.deskconn.deskconnd.pairing.generate")
        await self.register(self._authenticate, 'org.deskconn.deskconnd.authenticate')

    def is_local(self, auth_id, auth_role, realm):
        return self._principle.auth_id == auth_id and self._principle.auth_role == auth_role and \
               self._principle.realm == realm

    async def _authenticate(self, realm, authid, auth_details):
        assert auth_details.get('authmethod') == 'cryptosign'
        self.log.info("authenticating session with public key = {pubkey}", pubkey=authid)
        if self.is_local(authid, auth_details.get("authrole"), realm):
            return {
                'pubkey': auth_details.get("authextra").get("pubkey"),
                'realm': realm,
                'authid': authid,
                'role': auth_details.get("authrole"),
                'cache': True
            }
        principle = DB.get_principle(auth_id=authid, auth_role=auth_details.get("authrole"), realm=realm)
        if principle:
            return {
                'pubkey': authid,
                'realm': principle['realm'],
                'authid': authid,
                'role': principle['role'],
                'cache': True
            }
        raise ApplicationError('org.deskconn.deskconnd.no_such_user', 'no principal with matching public key')

    async def _generate(self):
        key = str(random.randint(100000, 999999))
        self._pending_otps.append(key)
        txaio.call_later(60, self._revoke_otp, key)
        return key

    def _revoke_otp(self, otp):
        if otp in self._pending_otps:
            self._pending_otps.remove(otp)
