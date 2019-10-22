import os

from setuptools import setup


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

VERSION = '0.1.0'

setup(
    name='deskconnd',
    version=VERSION,
    packages=['deskconnd', 'deskconnd.components', 'deskconnd.database'],
    url='https://github.com/deskconn/deskconnd',
    license='GNU GPL Version 3',
    author='Omer Akram',
    author_email='om26er@gmail.com',
    description='Expose your desktop functionality over the network.',
    download_url='https://github.com/deskconn/deskconnd/tarball/{}'.format(VERSION),
    keywords=['IPC', 'python'],
)
