# upload.py
import os, time
from joringels.src.joringels import Joringel
import joringels.src.settings as sts
import importlib


def run(
    srcAdapt,
    conAdapt,
    *args,
    action,
    projectName: str,
    host: str = None,
    retain=True,
    delay=1,
    **kwargs,
) -> None:
    """
    NOTE: NON-DIGESTIVE, encrypted secretsFile remains in .ssp
    imports secrets from source, stores it in .ssp and then uploads it to remote host
    NOTE: this is only allowed on a local host computer

    run like: joringels upload_all -n digiserver -src kdbx -con scp
    """
    # get secret
    assert projectName is not None, f"Specify -pr projectName or -pr all"
    sec = srcAdapt.main(*args, **kwargs)
    print(f"sleeping for {delay} seconds...")
    time.sleep(delay)
    for target, targetPath in sec.targets.items():
        if projectName != "all" and not (projectName in target or projectName in targetPath):
            print(f"Not uploading {target, targetPath} is not {projectName}")
            continue
        serverCreds = sec.load(*args, host=target, **kwargs)
        # encrypt secret
        kwargs.update({"key": sec.encrpytKey})
        j = Joringel(*args, **kwargs)
        encryptPath, _ = j._digest(*args, action=action, retain=retain, **kwargs)
        # upload to server
        print(f"Uploading {projectName}: {encryptPath}")
        scp = conAdapt.main(*args, **kwargs)
        # uploading secrets
        scp.upload(serverCreds, *args, **kwargs)
        # uploading _joringels.yml file
        joringels_params_upload(j, scp, serverCreds, *args, **kwargs)

    if not encryptPath:
        import colorama as color
        color.init()
        msg = f"jo upload: No upload parameter found. Check your datasafe params!"
        print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
    return encryptPath

def joringels_params_upload(j, scp, serverCreds, *args, **kwargs):
    # uploading startup params to ressources folder
    fileName = sts.appParamsFileName.replace(sts.fext, '.json')
    filePath = os.path.join(sts.encryptDir, fileName)
    with sts.temp_secret(j, *args, secretsFilePath=filePath, 
                                    entryName=sts.appParamsFileName, **kwargs) as s:
        scp.upload( 
                    serverCreds,
                    filePath,
                    os.path.dirname(filePath),
                    *args,
                    **kwargs,
        )

def main(*args, source: str, connector: str, safeName: str, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    kwargs['action'] = kwargs.get('action', 'upload')
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
