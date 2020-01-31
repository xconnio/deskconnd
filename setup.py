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

import os

from setuptools import setup


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

VERSION = '0.4'

setup(
    name='deskconnd',
    version=VERSION,
    packages=['deskconnd', 'deskconnd.components', 'deskconnd.database'],
    url='https://github.com/deskconn/deskconnd',
    license='GNU GPL Version 3',
    author='Omer Akram',
    author_email='om26er@gmail.com',
    description='Secure, cross-platform IPC on the network.',
    download_url='https://github.com/deskconn/deskconnd/tarball/{}'.format(VERSION),
    keywords=['IPC', 'python'],
    install_requires=['crossbar', 'appdirs', 'sqlalchemy', 'zeroconf', 'pyqrcode', 'autobahn[twisted,serialization]']
)
