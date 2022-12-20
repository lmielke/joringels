# helpers.py
from pathlib import Path
import json, os, sys, time, yaml
from contextlib import contextmanager
import joringels.src.settings as sts


def unalias_path(workPath: str) -> str:
    """
    repplaces path aliasse such as . ~ with path text
    """
    if not any([e in workPath for e in [".", "~", "%"]]):
        return workPath
    workPath = workPath.replace(r"%USERPROFILE%", "~")
    workPath = workPath.replace("~", os.path.expanduser("~"))
    if workPath.startswith(".."):
        workPath = os.path.join(os.path.dirname(os.getcwd()), workPath[3:])
    elif workPath.startswith("."):
        workPath = os.path.join(os.getcwd(), workPath[2:])
    workPath = os.path.normpath(os.path.abspath(workPath))
    return workPath


def prep_path(workPath: str, filePrefix=None) -> str:
    workPath = unalias_path(workPath)
    workPath = workPath if workPath.endswith(sts.fext) else f"{workPath}{sts.fext}"
    if os.path.isfile(workPath):
        return workPath
    if filePrefix:
        workPath = f"{filePrefix}_{workPath}"
    workPath = os.path.join(sts.encryptDir, workPath)
    workPath = workPath if workPath.endswith(sts.fext) else f"{workPath}{sts.fext}"
    return workPath


def mk_encrypt_path(safeName: str) -> str:
    encrpytPath = os.path.join(sts.encryptDir, f"{safeName.lower()}.yml")
    encrpytPath = encrpytPath.replace(".yml.yml", ".yml")
    return encrpytPath


def file_or_files(workPath: str, *args, **kwargs) -> list:
    """takes a name and checks if its a fileName or dirName
    then returns all files belongin to that file, dir
    i.e. chkey can change one dataSafe key or keys of all dataSafes in dir
    """
    workPath = prep_path(workPath)
    print(f"{workPath = }")
    if os.path.isdir(workPath):
        fileNames = os.listdir(workPath)
    elif os.path.isfile(workPath):
        workPath, fileName = os.path.split(workPath)
        fileNames = [fileName]
    return workPath, fileNames


@contextmanager
def temp_secret(j, *args, secretsFilePath: str, entryName: str, **kwargs) -> None:
    """
    temporaryly renames files in .ssp for upload to bypass files
    secretsFilePath: full path to secretsfile.json
    creds: joringels params to get secret
            {entryName: secretToWrite}
    """
    fType = os.path.splitext(secretsFilePath)[-1]
    try:
        secrets = j.secrets.get(entryName)
        with open(secretsFilePath, "w") as f:
            if fType == ".json":
                json.dump(secrets, f)
            elif fType == ".yml":
                yaml.dump(secrets, f)
            else:
                raise Exception(f"Invalid file extension: {fType}, use [.json, .yml]")
        while not os.path.exists(secretsFilePath):
            continue
        yield
    except Exception as e:
        print(f"oamailer.secrets_loader Exception: {e}")
    finally:
        if os.path.exists(secretsFilePath):
            os.remove(secretsFilePath)


@contextmanager
def temp_chdir(path: Path) -> None:
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """

    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


@contextmanager
def temp_ch_host_name(hostName: str) -> None:
    """Sets the cwd within the context
    Args:
        host (Path): The host to the cwd
    Yields:
        None
    """
    origin = os.environ.get("HOSTNAME", "")
    try:
        os.environ["HOSTNAME"] = hostName
        yield
    finally:
        os.environ["HOSTNAME"] = origin


@contextmanager
def temp_safe_rename(*args, safeName: str, prefix: str = "#", **kwargs) -> None:
    """
    temporaryly renames files in .ssp for upload to bypass files
    """
    # rename fileName by adding prefix
    fileName = f"{safeName.lower()}.yml"
    currPath = os.path.join(sts.encryptDir, fileName)
    tempPath = os.path.join(sts.encryptDir, f"{prefix}{fileName}")
    try:
        if os.path.exists(currPath):
            os.rename(currPath, tempPath)
        yield
    finally:
        if os.path.exists(tempPath):
            if os.path.exists(currPath):
                os.remove(currPath)
            time.sleep(0.1)
            os.rename(tempPath, currPath)
            time.sleep(0.1)


def get_api_enpoint_dir(connector, *args, **kwargs):
    with open(unalias_path(sts.available_appsPaths.get(os.name)), "r") as apps:
        available_apps = json.load(apps)
    app = available_apps.get(connector)
    if not app:
        raise Exception(f"no app found in available_apps.yml named {connector}")
    else:
        return (sts.api_endpoints_path(unalias_path(app[1]), connector), unalias_path(app[1]))
