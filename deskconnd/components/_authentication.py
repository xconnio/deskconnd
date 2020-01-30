#
# Copyright (C) 2018-2019 Omer Akram
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
                'role': auth_details.get("authrole")
            }

        principle = DB.get_principle(auth_id=authid, auth_role=auth_details.get("authrole"), realm=realm)

        if principle:
            return {
                'pubkey': authid,
                'realm': principle.realm,
                'authid': authid,
                'role': principle.auth_role
            }
        raise ApplicationError('org.deskconn.deskconnd.no_such_user', 'no principal with matching public key')

    async def generate_otp(self):
        key = str(random.randint(100000, 999999))
        self._pending_otps.append(key)
        txaio.call_later(60, self._revoke_otp, key)
        return key

    async def pair(self, otp, pubkey):
        if str(otp) in self._pending_otps:
            self._pending_otps.remove(str(otp))
            DB.add_principle(auth_id=pubkey, auth_role='deskconn', realm='deskconn')
            return True
        return False

    def _revoke_otp(self, otp):
        if otp in self._pending_otps:
            self._pending_otps.remove(otp)
