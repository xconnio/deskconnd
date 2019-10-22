import random

from autobahn.wamp.cryptobox import KeyRing
from autobahn.twisted.wamp import ApplicationSession
import txaio

from deskconnd.database.controller import DB


class PairingSession(ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        DB.refresh_local_principle(KeyRing().generate_key_hex(), config.realm, config.realm)

    def onConnect(self):
        principle = DB.get_local_principle()
        self.join(principle.realm, ["cryptosign"], principle.auth_id, principle.auth_role)

    async def onJoin(self, details):
        self.log.info('realm joined: {}'.format(details.realm))
        await self.register(self._generate, "org.deskconn.deskconnd.pairing.generate")

    async def _generate(self):
        key = random.randint(100000, 999999)
        DB.save_otp(key)
        txaio.call_later(60, DB.revoke_otp, key)
        return key
