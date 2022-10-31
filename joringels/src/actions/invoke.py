# serve.py
import os, yaml
from joringels.src.joringels import Joringel
from joringels.src.actions import fetch
from joringels.src.jorinde import Jorinde
import joringels.src.settings as sts


def api(*args, apiName:str, data:dict, **kwargs) -> dict:
    kwargs.update(get_params(*args, apiName=apiName, **kwargs))
    r = Jorinde(*args, **kwargs)
    secret = r._fetch(*args, safeName=apiName, entryName=data, **kwargs)
    return secret

def get_params(*args, apiName:str, host:str=None, port:int=None, **kwargs) -> dict:
    params = fetch.alloc(safeName=apiName, entryName='kwargs', retain=True)
    if host is not None:
        params['host'] = host
    if port is not None:
        params['port'] = port
    return params

def main(*args, data, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    assert data is not None, f"missing value for '-e data'"
    secret = api(*args, data=data, **kwargs)
    return f"{secret}"