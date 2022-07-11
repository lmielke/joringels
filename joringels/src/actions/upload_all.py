# upload.py
import os
from joringels.src.joringels import Joringel
import joringels.src.settings as sts
import importlib


def run(secImp, scpImp, action: str, *args, host, **kwargs) -> None:
    """
    NOTE: NON-DIGESTIVE, encrypted secretsFile remains in .ssp
    imports secrets from source, stores it in .ssp and then uploads it to remote host
    NOTE: this is only allowed on a local host computer

    run like: joringels upload_all -n digiserver -src kdbx -con scp
    """
    # get secret
    sec = secImp.main(*args, **kwargs)
    for target in sec.targets:
        serverCreds = sec.load(*args, host=target, **kwargs)
        # encrypt secret
        kwargs.update({"key": sec.encrpytKey})
        filePath, _ = Joringel(*args, **kwargs)._digest(*args, **kwargs)
        # upload to server
        scpImp.main(*args, **kwargs).upload(serverCreds, *args, **kwargs)


def main(*args, source: str, connector: str, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    secImp = importlib.import_module(f"{sts.impStr}.sources.{source}")
    scpImp = importlib.import_module(f"{sts.impStr}.connectors.{connector}")
    return run(secImp, scpImp, *args, source=source, **kwargs)
