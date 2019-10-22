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


class OTP(Base):
    __tablename__ = 'otps'

    uid = Column(Integer, primary_key=True)
    otp = Column(Integer, unique=True)


Base.metadata.create_all(engine)
