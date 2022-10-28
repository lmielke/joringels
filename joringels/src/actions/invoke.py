# serve.py
import os, yaml
from joringels.src.joringels import Joringel
from joringels.src.jorinde import Jorinde
import joringels.src.settings as sts


def remote(*args, **kwargs) -> dict:
    r = Jorinde(*args, **kwargs)
    secret = r._fetch(*args, **kwargs)
    return secret


def main(*args, entryName, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    assert entryName is not None, f"missing value for '-e entryName'"
    secret = remote(*args, entryName=entryName, **kwargs)
    return f"{secret}"