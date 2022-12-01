# serve.py
import os, json
from joringels.src.joringels import Joringel
from joringels.src.jorinde import Jorinde
import joringels.src.settings as sts
import joringels.src.helpers as helpers


def local(*args, **kwargs) -> None:
    try:
        j = Joringel(*args, **kwargs)
        j._digest(*args, **kwargs)
        # if not j.authorized:
        #     raise Exception(f"Not authorized!")
    except Exception as e:
        print(f"show.local: {e}")
        return None
    return json.dumps(j.secrets, indent=4)


def main(*args, safeName, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    secret = local(*args, safeName=safeName, **kwargs)
    return f"{secret}"
