#
# Copyright (C) 2019-2020 Omer Akram
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

from tortoise.models import Model
from tortoise import fields


class Principle(Model):
    uid = fields.IntField(pk=True)
    access = fields.CharField(255, default='remote')
    auth_id = fields.CharField(255, unique=True)
    auth_role = fields.CharField(255)
    realm = fields.CharField(255)

    private_key = fields.CharField(255, null=True)


class StrKeyStrValue(Model):
    uid = fields.IntField(pk=True)
    key = fields.CharField(255, unique=True)
    value = fields.CharField(255, null=True)
