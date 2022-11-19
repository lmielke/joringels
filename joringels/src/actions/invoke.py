# serve.py
import os, yaml
from joringels.src.joringels import Joringel
from joringels.src.actions import fetch
from joringels.src.jorinde import Jorinde
import joringels.src.settings as sts


def api(*args, data:dict, **kwargs) -> dict:
    kwargs.update(get_params(*args, **kwargs))
    r = Jorinde(*args, **kwargs)
    response = r._fetch(*args, entryName=data, **kwargs)
    return response

def get_params(*args, clusterName:str, connector:str, host:str=None, port:int=None, retain:str=None, **kwargs) -> dict:
    # clustername is required here for joringels._prep_secrets to get cluster params
    params = fetch.alloc(*args, entryName=clusterName, clusterName=clusterName, connector=connector, retain=True, **kwargs )
    params = params.get(sts.cluster_params).get(sts.apiParamsFileName).get(connector)
    host = host if host is not None else params[sts.providerHost]
    port = port if port is not None else int(params.get('ports')[0].split(':')[0])
    return {'host': host, 'port': port}

def main(*args, data, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    assert data is not None, f"missing value for '-e data'"
    secret = api(*args, data=data, **kwargs)
    return f"{secret}"