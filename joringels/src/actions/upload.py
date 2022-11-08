# upload.py
# jo upload -n timesheet_testing -src kdbx -con scp -pr all
import os, time
from joringels.src.joringels import Joringel
import joringels.src.settings as sts
import importlib


def run(
    sourceAdapter,
    conAdapt,
    *args,
    action,
    projectName: str,
    host: str = None,
    **kwargs,
) -> None:
    """
    NOTE: NON-DIGESTIVE, encrypted secretsFile remains in .ssp
    imports secrets from source, stores it in .ssp and then uploads it to remote host
    NOTE: this is only allowed on a local host computer


    jo upload -n timesheet_testing -src kdbx -con scp -pr joringels
    jo upload -n timesheet_testing -src kdbx -con scp -pr all


    """
    # get secret
    checks(*args, projectName=projectName, **kwargs)
    
    sec = sourceAdapter.main(*args, **kwargs)
    # decrypted_secret.yml
    dataSafePath = load_data_safe(sec, *args, **kwargs)
    targets = get_targets(sec.secrets, *args, projectName=projectName, **kwargs)
    kwargs.update({"key": sec.secrets.get(sts.clusters_params).get('password')})

    j, encryptPath = encrypt_secrets(*args, action=action, **kwargs)
    upload_targets(j, conAdapt, targets, encryptPath, *args, projectName=projectName, **kwargs)

    if not encryptPath:
        import colorama as color
        color.init()
        msg = f"jo upload: No upload parameter found. Check your datasafe params!"
        print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
    return encryptPath

def upload_targets(j, conAdapt, targets, encryptPath, *args, projectName, **kwargs):
    for targetName, target in zip(*targets):
        # upload to server
        print(f"Uploading {targetName}: {target}")
        scp = conAdapt.main(*args, **kwargs)
        scp.upload(encryptPath, *args, **target)

def encrypt_secrets(*args, **kwargs):
    j = Joringel(*args, **kwargs)
    encryptPath, _ = j._digest(*args, retain=True, **kwargs)
    return j, encryptPath


def checks(*args, projectName, **kwargs):
    if projectName is None:
        print(f"Specify -pr projectName or -pr all")
        exit()

def get_targets(secrets, *args, projectName, safeName, **kwargs):
    targetPaths = secrets.get(safeName).get(sts.safeParamsFileName)['targets']
    # filter targets by projectNames
    if projectName == 'all':
        targetEntries = [t for t in targetPaths]
    else:
        targetEntries = [t for t in targetPaths if projectName in t]
    targets = [secrets[tn.split('/')[-1]] for tn in targetEntries]
    targetNames = [tn.split('/')[-2] for tn in targetEntries]
    return targetNames, targets

def load_data_safe(sec, *args, connector:str=None, **kwargs):
    dataSafePath = sec.load(*args, connector='kdbx', **kwargs)
    return dataSafePath

def main(*args, source: str, connector: str, safeName: str, retain: bool=True, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    kwargs['action'] = kwargs.get('action', 'upload')
    isPath = os.path.isfile(source)
    sourceAdapter = importlib.import_module(
        f"{sts.impStr}.sources.{source.split('.')[-1] if isPath else source}"
    )
    conAdapt = importlib.import_module(f"{sts.impStr}.connectors.{connector}")
    # upload will temporaryly rename existing dataSafe with name identical to uploaded safe
    with sts.temp_safe_rename(*args, prefix="#upload_", safeName=safeName, **kwargs) as t:
        encryptPath = run(sourceAdapter, conAdapt, *args, source=source, safeName=safeName, **kwargs)
        if os.path.exists(encryptPath):
            os.remove(encryptPath)
    return True
