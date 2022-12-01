# serve.py
# from joringels.src.actions import fetch
# fetch.alloc(**{'entryName': 'testing', 'retain': True})
import os
from joringels.src.joringels import Joringel
from joringels.src.jorinde import Jorinde
import joringels.src.settings as sts
import joringels.src.helpers as helpers


def remote(*args, **kwargs) -> dict:
    r = Jorinde(*args, **kwargs)
    secret = r._fetch(*args, **kwargs)
    return secret


def local(*args, entryName, **kwargs) -> dict:
    try:
        j = Joringel(*args, **kwargs)
        j._digest(*args, **kwargs)
        if not j.authorized:
            raise Exception(f"fetch.local, Not authorized!")
    except Exception as e:
        print(f"fetch.local: {e}")
        return None
    return j.secrets.get(entryName)


def alloc(*args, host=None, **kwargs):
    if host == "loc" or host is None:
        if secret := local(*args, **kwargs):
            return secret
        elif host == "loc":
            print(f"fetch.alloc, Entry not found locally: {secret = }")
            return None
    if secret := remote(*args, host=host, **kwargs):
        return secret
    else:
        return None


def main(*args, entryName, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    assert entryName is not None, f"missing value for '-e entryName'"
    if entryName.isnumeric():
        entryName = int(entryName)
    secret = alloc(*args, entryName=entryName, **kwargs)
    return f"{secret}"
