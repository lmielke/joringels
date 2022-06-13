# upload.py
import os
from joringels.src.jorinde import Jorinde
from joringels.src.joringels import Joringel
import joringels.src.settings as sts
import importlib


def run(secImp: object, action: str, *args, host, **kwargs) -> None:
    """
    imports secrets from source and unpacks it into .ssp folder
    NOTE: NON-DIGESTIVE, encrypted secretsFile remains in .ssp
    NOTE: this leaves unprotected secrets in .ssp
    NOTE: this is only allowed on a local host computer

    run like: joringels unprotectedload -g digiserver -src keepass
    """
    sec = secImp.main(*args, **kwargs)
    sec.load(*args, filePrefix=f"{action}_", **kwargs)
    Jorinde(*args, **kwargs)._unpack_decrypted(*args, **kwargs)


def main(*args, source: str, connector: str, **kwargs) -> None:
    """
    imports source
    then runs unprotected load process using imported source an connector
    """
    secImp = importlib.import_module(f"{sts.impStr}.sources.{source}")
    return run(secImp, *args, **kwargs)
