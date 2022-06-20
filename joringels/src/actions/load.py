# upload.py
import os

from joringels.src.joringels import Joringel
import joringels.src.settings as sts
import importlib


def run(secImp: object, action: str, *args, **kwargs) -> None:
    """
    imports secrets from source and saves it into .ssp folder
    NOTE: NON-DIGESTIVE, encrypted secretsFile remains in .ssp
    NOTE: this is only allowed on a local host computer

    run like: joringels load -n digiserver -src kdbx
    """
    # get secret
    sec = secImp.main(*args, **kwargs)
    sec.load(*args, **kwargs)
    # encrypt secret
    kwargs.update({"key": sec.encrpytKey})
    filePath, _ = Joringel(*args, **kwargs)._digest(*args, **kwargs)
    return filePath


def main(*args, source: str, connector: str, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs load process using imported source an connector
    """
    if os.path.isfile(source):
        moduleName = os.path.splitext(source)[-1][1:]
    else:
        moduleName = source
    secImp = importlib.import_module(f"{sts.impStr}.sources.{moduleName}")
    return run(secImp, *args, source=source, **kwargs)
