# upload.py
import os
from joringels.src.joringels import Joringel
import joringels.src.settings as sts
import importlib


def run(srcAdapt, conAdapt, action: str, *args, host, **kwargs) -> None:
    """
    NOTE: NON-DIGESTIVE, encrypted secretsFile remains in .ssp
    imports secrets from source, stores it in .ssp and then uploads it to remote host
    NOTE: this is only allowed on a local host computer

    run like: joringels upload_all -n digiserver -src kdbx -con scp
    """
    # get secret
    sec = srcAdapt.main(*args, **kwargs)
    for target in sec.targets:
        serverCreds = sec.load(*args, host=target, **kwargs)
        # encrypt secret
        kwargs.update({"key": sec.encrpytKey})
        encryptPath, _ = Joringel(*args, **kwargs)._digest(*args, **kwargs)
        # upload to server
        conAdapt.main(*args, **kwargs).upload(serverCreds, *args, **kwargs)
    return encryptPath


def main(*args, source: str, connector: str, safeName=None, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    assert safeName is not None, f"missing value for '-n safeName'"
    isPath = os.path.isfile(source)
    srcAdapt = importlib.import_module(
        f"{sts.impStr}.sources.{source.split('.')[-1] if isPath else source}"
    )
    conAdapt = importlib.import_module(f"{sts.impStr}.connectors.{connector}")
    # upload will temporaryly rename existing dataSafe with name identical to uploaded safe
    with sts.temp_safe_rename(*args, prefix="#upload_", safeName=safeName, **kwargs) as t:
        encryptPath = run(srcAdapt, conAdapt, *args, source=source, safeName=safeName, **kwargs)
        if os.path.exists(encryptPath):
            os.remove(encryptPath)
    return True
