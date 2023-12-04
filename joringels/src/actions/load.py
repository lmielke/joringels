# upload.py
import os, time

from joringels.src.joringels import Joringel
import joringels.src.settings as sts
import joringels.src.helpers as helpers
import importlib

import colorama as color


def run(srcAdapt: object, action: str, *args, **kwargs) -> None:
    """
    imports secrets from source and saves it into .ssp folder
    NOTE: NON-DIGESTIVE, encrypted secretsFile remains in .ssp
    NOTE: this is only allowed on a local host computer

    run like:
    jo load -n safe_one -pd wobbles -cn testing -src kdbx
    -n: safeName
    -pd: productName (needed to locate correct cluster)
    -cn: clusterName to load secrets for


    """
    j = Joringel(*args, **kwargs)
    # get secret
    with srcAdapt.KeePassSecrets("load", *args, **kwargs) as src:
        secrets = src.read_source(*args, **kwargs)
        j.create(j.encryptPath, secrets, *args, **kwargs)


def main(*args, source: str, **kwargs) -> None:
    """
    imports source from src argument
    then runs load process using imported source
    """
    # sometimes windows adds a ; to env variables
    source = source.strip(";")
    # if source looks like a path
    if os.sep in source.replace("/", os.sep):
        if os.path.isfile(source):
            moduleName = os.path.splitext(source)[-1][1:]
        else:
            assert False, f"{color.Fore.RED}source: {source} is not a file{color.Style.RESET_ALL}"
    else:
        moduleName = source
    srcAdapt = importlib.import_module(f"joringels.src.sources.{moduleName}")
    return run(srcAdapt, *args, source=source, **kwargs)
