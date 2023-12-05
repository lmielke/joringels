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
            raise Exception(f"ERROR: fetch.local, Not authorized!")
    except Exception as e:
        print(f"ERROR: fetch.local: {e}")
        return None
    return j.secrets.get(entryName)


def get_nested_value(nested_dict, keys):
    """
    you can fetch a value like this:
        jo fetch -e testing.cluster_params._joringels.DATASAFEIP
    In this case fetch will split the dotted string and follow the resulting path to
    the lowest key.

    """
    current_value = nested_dict
    try:
        for key in keys:
            current_value = current_value[key]
        return current_value
    except (KeyError, TypeError):
        return False
    return False


def alloc(*args, host=None, **kwargs):
    if host == "loc" or host is None:
        if secret := local(*args, **kwargs):
            return secret
        elif host == "loc":
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
    entries = entryName.split(".", 1)
    subSecret = None
    if entries[0].isnumeric():
        entryName = int(entries[0])
    secret = alloc(*args, entryName=entries[0], **kwargs)
    if len(entries) >= 2:
        # jo fetch -e testing.cluster_params._joringels.DATASAFEIP
        # the dotted string above results in a list of keys that can be followed down the dict
        subSecret = get_nested_value(secret, entries[1].split("."))
    return secret if subSecret is None else subSecret
