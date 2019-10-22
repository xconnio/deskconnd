from deskconnd.database.schema import Principle, OTP
from deskconnd.database.base import Session


class DB:
    __session = None

    @staticmethod
    def get_instance():
        if not DB.__session:
            DB.__session = Session(autocommit=True)
        return DB.__session

    def __init__(self):
        raise RuntimeError("Should not be instantiated directly, rather call DB.get_instance()")

    @staticmethod
    def add_principle(auth_id, auth_role, realm, access='remote', private_key=None):
        principle = Principle(auth_id=auth_id, auth_role=auth_role, realm=realm, access=access, private_key=private_key)
        DB.get_instance().add(principle)
        return principle

    @staticmethod
    def get_principle(auth_id, auth_role, realm):
        principle = DB.get_instance().query(Principle).filter(
            Principle.auth_id == auth_id, Principle.auth_role == auth_role, Principle.realm == realm).first()
        return principle

    @staticmethod
    def get_local_principle():
        return DB.get_instance().query(Principle).filter(Principle.access == 'local').first()

    @staticmethod
    def refresh_local_principle(key_pair, auth_role, realm):
        DB.get_instance().query(Principle).filter(Principle.access == 'local').delete()
        return DB.add_principle(auth_id=key_pair[1], auth_role=auth_role, realm=realm, access='local',
                                private_key=key_pair[0])

    @staticmethod
    def save_otp(otp):
        DB.get_instance().add(OTP(otp=otp))

    @staticmethod
    def revoke_otp(otp):
        DB.get_instance().query(OTP).filter(OTP.otp == otp).delete()
