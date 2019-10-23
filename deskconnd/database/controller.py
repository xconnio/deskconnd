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

from deskconnd.database.schema import Principle, StrKeyStrValue
from deskconnd.database.base import Session


class DB:
    __session = None

    @staticmethod
    def _get_instance():
        if not DB.__session:
            DB.__session = Session()
        return DB.__session

    @staticmethod
    def put_string(key, value):
        item = DB._get_instance().query(StrKeyStrValue).filter(StrKeyStrValue.key == key).first()
        if item:
            item.value = value
        else:
            DB._get_instance().add(StrKeyStrValue(key=key, value=value))
        DB._get_instance().commit()

    @staticmethod
    def get_string(key, default=None):
        item = DB._get_instance().query(StrKeyStrValue).filter(StrKeyStrValue.key == key).first()
        if item:
            return item.value
        return default

    @staticmethod
    def put_boolean(key, value):
        assert isinstance(value, bool)
        DB.put_string(key, str(value))

    @staticmethod
    def get_boolean(key, default=True):
        value = DB.get_string(key)
        if value is None:
            return default

        if value.lower() == 'true':
            return True
        return False

    @staticmethod
    def is_first_run():
        return DB.get_boolean("first_run", True)

    @staticmethod
    def init_config():
        if DB.is_first_run():
            uid = str(uuid.uuid4())
            DB.put_string("uid", uid)
            DB.put_boolean("first_run", False)
            return uid
        return DB.get_string("uid")

    @staticmethod
    def add_principle(auth_id, auth_role, realm, access='remote', private_key=None):
        principle = Principle(auth_id=auth_id, auth_role=auth_role, realm=realm, access=access,
                              private_key=private_key)
        DB._get_instance().add(principle)
        DB._get_instance().commit()
        return principle

    @staticmethod
    def get_principle(auth_id, auth_role, realm):
        return DB._get_instance().query(Principle).filter(
            Principle.auth_id == auth_id, Principle.auth_role == auth_role, Principle.realm == realm).first()

    @staticmethod
    def get_local_principle():
        return DB._get_instance().query(Principle).filter(Principle.access == 'local').first()

    @staticmethod
    def refresh_local_principle(key_pair, auth_role, realm):
        item = DB._get_instance().query(Principle).filter(Principle.access == 'local').first()
        if item:
            DB._get_instance().delete(item)
            DB._get_instance().commit()
        return DB.add_principle(auth_id=key_pair[1], auth_role=auth_role, realm=realm, access='local',
                                private_key=key_pair[0])

    @staticmethod
    def toggle_discovery(enabled):
        DB.put_boolean("discovery", enabled)

    @staticmethod
    def is_discovery_enabled():
        return DB.get_boolean("discovery", True)
