#
# Copyright (C) 2019 Omer Akram
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

import uuid

from tortoise import Tortoise

from deskconnd.database.schema import Principle, StrKeyStrValue
from deskconnd.database.base import get_db_path


class DB:
    @staticmethod
    async def put_string(key, value):
        item = await StrKeyStrValue.filter(key=key).first()
        if item:
            item.value = value
            await item.save()
        else:
            await StrKeyStrValue.create(key=key, value=value)

    @staticmethod
    async def get_string(key, default=None):
        item = await StrKeyStrValue.filter(key=key).first()
        if item:
            return item.value
        return default

    @staticmethod
    async def put_boolean(key, value):
        assert isinstance(value, bool)
        await DB.put_string(key, str(value))

    @staticmethod
    async def get_boolean(key, default=True):
        value = await DB.get_string(key)
        if value is None:
            return default

        if value.lower() == 'true':
            return True
        return False

    @staticmethod
    async def is_first_run():
        return await DB.get_boolean("first_run", True)

    @staticmethod
    async def init_config():
        if await DB.is_first_run():
            uid = str(uuid.uuid4())
            await DB.put_string("uid", uid)
            await DB.put_boolean("first_run", False)
            return uid
        return await DB.get_string("uid")

    @staticmethod
    async def add_principle(auth_id, auth_role, realm, access='remote', private_key=None):
        return await Principle.create(auth_id=auth_id, auth_role=auth_role, realm=realm, access=access,
                                      private_key=private_key)

    @staticmethod
    async def get_principle(auth_id, auth_role, realm):
        return await Principle.filter(auth_id=auth_id, auth_role=auth_role, realm=realm).first()

    @staticmethod
    async def get_local_principle():
        return await Principle.filter(access='local').first()

    @staticmethod
    async def refresh_local_principle(key_pair, auth_role, realm):
        item = await Principle.filter(access='local').first()
        if item:
            await item.delete()
        return await DB.add_principle(auth_id=key_pair[1], auth_role=auth_role, realm=realm, access='local',
                                      private_key=key_pair[0])

    @staticmethod
    async def toggle_discovery(enabled):
        await DB.put_boolean("discovery", enabled)

    @staticmethod
    async def is_discovery_enabled():
        return await DB.get_boolean("discovery", True)

    @staticmethod
    async def init_db():
        await Tortoise.init(db_url=f'sqlite://{get_db_path()}', modules={'models': ['deskconnd.database.schema']})
        await Tortoise.generate_schemas()
        print("Database ready...")
