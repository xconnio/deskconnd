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

from sqlalchemy import Column, Integer, String

from deskconnd.database.base import Base, engine


class Principle(Base):
    __tablename__ = 'principles'

    uid = Column(Integer, primary_key=True)
    access = Column(String(255), default='remote')
    auth_id = Column(String(255), nullable=False, unique=True)
    auth_role = Column(String(255), nullable=False)
    realm = Column(String(255), nullable=False)

    private_key = Column(String(255), nullable=True)


class StrKeyStrValue(Base):
    __tablename__ = 'str_key_str_value'

    uid = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False, unique=True)
    value = Column(String(255), nullable=True)


Base.metadata.create_all(engine)
