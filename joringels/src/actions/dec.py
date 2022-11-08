# serve.py
import os, json
from joringels.src.joringels import Joringel
from joringels.src.jorinde import Jorinde
import joringels.src.settings as sts

def local(*args, **kwargs) -> None:
    try:
        j = Joringel(*args, **kwargs)
        j._digest(*args, **kwargs)
        # if not j.authorized:
        #     raise Exception(f"Not authorized!")
    except Exception as e:
        print(f"show.local: {e}")
        return None
    with open(os.path.join(sts.encryptDir, 'initialize.json'), 'w+') as f:
        json.dump(j.secrets, f)

def main(*args, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    secret = local(*args, **kwargs)
    return f"{secret}"