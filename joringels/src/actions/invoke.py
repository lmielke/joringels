# serve.py
import os, yaml
from joringels.src.joringels import Joringel
from joringels.src.actions import fetch
from joringels.src.jorinde import Jorinde
import joringels.src.settings as sts


def api(*args, data:dict, **kwargs) -> dict:
    # kwargs.update(get_params(*args, **kwargs))
    r = Jorinde(*args, **kwargs)
    response = r._fetch(*args, entryName=data, **kwargs)
    return response

# def get_params(*args, clusterName:str, connector:str, host:str=None, port:int=None, retain:str=None, **kwargs) -> dict:
#     """ 
#         gets all invokation relevant parameters like passwords, port, host
#     """
#     params = fetch.alloc(*args, 
#                                 entryName=clusterName, 
#                                 # jo._prep_secrets needs cluster specific jo params
#                                 clusterName=clusterName, 
#                                 connector=connector, 
#                                 retain=True,
#                                 **kwargs )
#     params = params.get(sts.cluster_params).get(sts.apiParamsFileName).get(connector)
    
#     # NOTE this is not in the correct module ! should be in get_soc.py
#     # if client host is a dev PC then use localhost, else get secretsHost from secrets data
#     secretsHost = params['networks'][list(params['networks'].keys())[0]][sts.providerHost]
#     host = host if host is not None else 'localhost' if os.name == 'nt' else secretsHost
#     # port reads docker-compose host mapping and converts port num literal to int
#     port = port if port is not None else int(params.get('ports')[0].split(':')[0])
#     return {'host': host, 'port': port}

def main(*args, data, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    assert data is not None, f"missing value for '-e data'"
    secret = api(*args, data=data, **kwargs)
    return f"{secret}"