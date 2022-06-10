from uuid import uuid1


def get_unique_id() -> str:
    """Get uuid unique id for filename."""
    uid = str(uuid1().int)[:11]
    return uid
