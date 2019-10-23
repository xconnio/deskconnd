from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp import ApplicationError
from autobahn.wamp.cryptobox import KeyRing

from deskconnd.database.controller import DB
from deskconnd.components._discovery import Discovery
from deskconnd.components._authentication import Authentication


class ManagementSession(ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self._system_uid = DB.init_config()
        self._principle = DB.refresh_local_principle(KeyRing().generate_key_hex(), config.realm, config.realm)

        self._discovery = Discovery(config.realm, self._system_uid)
        self._auth = Authentication(self._principle)

    def onConnect(self):
        self.join(self._principle.realm, ["cryptosign"], self._principle.auth_id, self._principle.auth_role)

    async def onJoin(self, details):
        self.log.info('realm joined: {}'.format(details.realm))
        await self.register(self._auth.generate_otp, "org.deskconn.deskconnd.pair")
        await self.register(self._auth.authenticate, 'org.deskconn.deskconnd.authenticate')
        await self.register(self._toggle_discovery, 'org.deskconn.deskconnd.toggle_discovery')

        if DB.is_discovery_enabled():
            self._discovery.start()

    def onLeave(self, details):
        self._discovery.stop()

    async def _toggle_discovery(self, enabled):
        if type(enabled) != bool:
            raise ApplicationError("enabled must be a boolean")

        if enabled:
            self._discovery.start()
        else:
            self._discovery.stop()
