# serve.py
import os, yaml
from joringels.src.joringels import Joringel
from joringels.src.jorinde import Jorinde
import joringels.src.settings as sts


def remote(*args, **kwargs) -> dict:
    j = Jorinde(*args, **kwargs)
    secret = j._fetch(*args, **kwargs)
    return secret


def local(*args, entry, **kwargs) -> dict:
    try:
        j = Joringel(*args, **kwargs)
        j._digest(*args, **kwargs)
        secret = j.secrets[entry]
    except Exception as e:
        return None
    return secret


def alloc(*args, **kwargs):
    if secret := local(*args, **kwargs):
        return secret
    elif secret := remote(*args, **kwargs):
        return secret
    else:
        return None


def main(*args, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    return alloc(*args, **kwargs)
