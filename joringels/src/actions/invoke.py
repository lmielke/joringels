# serve.py
import os, yaml
from joringels.src.actions import fetch
import joringels.src.settings as sts
import joringels.src.helpers as helpers


def api(*args, data: dict, **kwargs) -> dict:
    from joringels.src.jorinde import Jorinde

    # kwargs.update(get_params(*args, **kwargs))
    r = Jorinde(*args, **kwargs)
    response = r._fetch(*args, entryName=data, **kwargs)
    return response


def local(*args, data: dict, **kwargs) -> dict:
    from joringels.src.joringels_server import JoringelsServer

    js = JoringelsServer(*args, **kwargs)
    js.server(*args, **kwargs)
    js.run_api(*args, **data, **kwargs)


def main(*args, data, host=None, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    assert data is not None, f"missing value for '-e data'"
    if host == "loc":
        secret = local(*args, data=data, **kwargs)
    else:
        secret = api(*args, data=data, **kwargs)
    return f"{secret}"
