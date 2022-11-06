# serve.py
import os, yaml
from joringels.src.joringels import Joringel
from joringels.src.actions import fetch
from joringels.src.jorinde import Jorinde
import joringels.src.settings as sts


def api(*args, cluster:str, data:dict, **kwargs) -> dict:
    kwargs.update(get_params(*args, cluster=cluster, **kwargs))
    r = Jorinde(*args, **kwargs)
    secret = r._fetch(*args, safeName=cluster, entryName=data, **kwargs)
    return secret

def get_params(*args, cluster:str, host:str=None, port:int=None, connector:str, **kwargs) -> dict:
    params = fetch.alloc(
                            safeName=cluster, 
                            entryName='_apis.yml', 
                            connector=connector,
                            retain=True,
                            )
    params['HOST'] = host if host is not None else params['SERVERNAME']
    if port is not None: params['PORT'] = port
    return params

def main(*args, data, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    assert data is not None, f"missing value for '-e data'"
    secret = api(*args, data=data, **kwargs)
    return f"{secret}"