# upload.py
import os
from joringels.src.jorinde import Jorinde
from joringels.src.joringels import Joringel
import joringels.src.settings as sts
import joringels.src.helpers as helpers
import importlib


def run(srcAdapt: object, action: str, *args, host, **kwargs) -> None:
    """
    imports secrets from source and unpacks it into .ssp folder
    NOTE: NON-DIGESTIVE, encrypted secretsFile remains in .ssp
    NOTE: this leaves unprotected secrets in .ssp
    NOTE: this is only allowed on a local host computer

    run like: joringels unprotectedload -n safe_one -src kdbx
    """
    sec = srcAdapt.main(*args, **kwargs)
    sec.load(*args, filePrefix=f"{action}_", **kwargs)
    Jorinde(*args, **kwargs)._unpack_decrypted(*args, **kwargs)


def main(*args, source: str, connector: str, **kwargs) -> None:
    """
    imports source
    then runs unprotected load process using imported source an connector
    """
    if os.path.isfile(source):
        moduleName = os.path.splitext(source)[-1][1:]
    else:
        moduleName = source
    srcAdapt = importlib.import_module(f"joringels.src.sources.{moduleName}")
    return run(srcAdapt, *args, source=source, **kwargs)
