# serve.py
import json, os, yaml
from joringels.src.actions import fetch
import joringels.src.settings as sts
import joringels.src.helpers as helpers


def api_call(*args, data: dict, **kwargs) -> dict:
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


def prep_data(api, entryName):
    assert (
        api is not None and entryName is not None
    ), f"ERROR: missing value for '-e entryName or data'"
    nData, data = json.loads(entryName.replace("'", '"')), {}
    if "payload" in nData.keys():
        data["payload"] = nData["payload"]
    else:
        data["payload"] = nData
    assert api not in nData.keys(), f"ERROR: api name {api} already exists in nData: {nData}"
    data["api"] = api
    print(f"data: {data}")
    return data


def main(*args, api=None, data=None, host=None, entryName=None, connector=None, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    assert data is not None or entryName is not None, f"missing value for '-e entryName or data'"
    assert connector is not None, f"missing value for '-con connector'"
    print(f"{connector = }")
    # main might be called from the command line in which case --entryName and --data is provided
    if entryName is not None:
        data = prep_data(api, entryName)
    # invoke can be done locally or remote
    if host == "loc":
        secret = local(*args, data=data, connector=connector, **kwargs)
    else:
        secret = api_call(*args, data=data, connector=connector, **kwargs)
    return f"{secret}"
