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
