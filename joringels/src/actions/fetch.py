# serve.py
import os, yaml
from joringels.src.jorinde import Jorinde
import joringels.src.settings as sts


def remote(*args, **kwargs) -> dict:
    j = Jorinde(*args, **kwargs)
    secret = j._fetch(*args, **kwargs)
    return secret


def local(*args, client, **kwargs) -> dict:
    try:
        with open(sts.prep_path(os.path.join(sts.encryptDir, client)), "r") as f:
            secret = yaml.safe_load(f)
    except FileNotFoundError:
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
