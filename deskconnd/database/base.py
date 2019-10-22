import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from deskconnd.environment import is_snap

DB_FILE = "database.sqlite"


def get_db_path():
    if is_snap():
        return os.path.join(os.path.expandvars("$SNAP_COMMON"), DB_FILE)
    return os.path.join(os.path.expandvars("$HOME"), DB_FILE)


engine = create_engine(f'sqlite:///{get_db_path()}')
Session = sessionmaker(bind=engine)
Base = declarative_base()
