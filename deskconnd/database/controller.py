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

from sqlitedict import SqliteDict

from deskconnd.database.schema import Principle
from deskconnd.database.base import get_db_path


class DB:

    def __init__(self) -> None:
        super().__init__()
        self.db: SqliteDict = SqliteDict(get_db_path(), autocommit=True)

    def put_string(self, key: str, value):
        assert isinstance(key, str)
        assert isinstance(value, str)
        self.db[key] = value

    def get_string(self, key: str, default=None):
        assert isinstance(key, str)
        assert isinstance(default, str) or default is None
        return self.db.get(key, default)

    def put_boolean(self, key: str, value: bool):
        assert isinstance(key, str)
        assert isinstance(value, bool)
        self.db[key] = value

    def get_boolean(self, key, default=True):
        assert isinstance(key, str)
        assert isinstance(default, bool)
        return self.db.get(key, default)

    def is_first_run(self):
        return self.get_boolean('first_run', True)

    def init_config(self):
        if self.is_first_run():
            uid = str(uuid.uuid4())
            self.db['uid'] = uid
            self.put_boolean('first_run', False)
            return uid

        return self.get_string('uid')

    def add_principle(self, auth_id, auth_role, realm, access='remote', private_key=None):
        principle = Principle(auth_id, auth_role, realm, access, private_key)
        self.db[auth_id] = principle
        return principle

    def get_principle(self, auth_id):
        return self.db.get(auth_id)

    def get_local_principle(self):
        return self.db.get('local_principle')

    def refresh_local_principle(self, key_pair, auth_role, realm):
        principle = Principle(key_pair[1], auth_role, realm, 'local', key_pair[0])
        self.db['local_principle'] = principle
        return principle

    def toggle_discovery(self, enabled):
        self.put_boolean('discovery', enabled)

    def is_discovery_enabled(self):
        return self.get_boolean('discovery', True)
