import os


def is_snap():
    return os.environ.get("SNAP_NAME") == "deskconnd"
