import random

from autobahn.wamp.exception import ApplicationError
import txaio

from deskconnd.database.controller import DB


class Authentication:
    def __init__(self, principle):
        self._principle = principle
        self._pending_otps = []
        self._log = txaio.make_logger()

    def _is_local(self, auth_id, auth_role, realm):
        return self._principle.auth_id == auth_id and self._principle.auth_role == auth_role and \
               self._principle.realm == realm

    async def authenticate(self, realm, authid, auth_details):
        assert auth_details.get('authmethod') == 'cryptosign'
        self._log.info("authenticating session with public key = {pubkey}", pubkey=authid)
        extras = auth_details.get("authextra")
        if self._is_local(authid, auth_details.get("authrole"), realm):
            return {
                'pubkey': extras.get("pubkey"),
                'realm': realm,
                'authid': authid,
                'role': auth_details.get("authrole"),
                'cache': True
            }
        if extras.get('otp') in self._pending_otps:
            principle = DB.add_principle(auth_id=authid, auth_role=auth_details.get("authrole"), realm=realm)
            self._pending_otps.pop(extras.get('otp'))
        else:
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

    async def generate_otp(self):
        key = str(random.randint(100000, 999999))
        self._pending_otps.append(key)
        txaio.call_later(60, self._revoke_otp, key)
        return key

    def _revoke_otp(self, otp):
        if otp in self._pending_otps:
            self._pending_otps.remove(otp)
