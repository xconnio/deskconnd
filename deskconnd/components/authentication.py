from autobahn.wamp import ApplicationError
from autobahn.twisted.wamp import ApplicationSession

from deskconnd.database.controller import DB


class AuthSession(ApplicationSession):
    async def onJoin(self, details):
        self.log.info('realm joined: {}'.format(details.realm))
        await self.register(self.authenticate, 'org.deskconn.deskconnd.authenticate')

    def is_local(self, auth_id, auth_role, realm):
        principle = DB.get_local_principle()
        return principle.auth_id == auth_id and principle.auth_role == auth_role and principle.realm == realm

    async def authenticate(self, realm, authid, auth_details):
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
        principal = DB.get_principle(auth_id=authid, auth_role=auth_details.get("authrole"), realm=realm)
        if principal:
            return {
                'pubkey': authid,
                'realm': principal['realm'],
                'authid': authid,
                'role': principal['role'],
                'cache': True
            }
        raise ApplicationError('org.deskconn.deskconnd.no_such_user', 'no principal with matching public key')
