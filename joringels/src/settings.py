# settings.py

# settings.py
import os, sys, yaml
from contextlib import contextmanager
from pathlib import Path


def unalias_path(path: str) -> str:
    path = path.replace(r"%USERPROFILE%", "~")
    path = path.replace("~", os.path.expanduser("~"))
    if path.startswith("."):
        path = os.path.join(os.getcwd(), path[2:]).replace("/", os.sep)
    return path


fext = ".yml"
# kdbx parameters you might want to change
# name of group in keeepass that stores data_safes entries
safeName = "joringels_data_safes"
# keepas/advanced/attachments
# name of params file containing sources an targets for your secrets
safeParamsFileName = f"safe_params{fext}"
# name of general file containing program params such as allowed hosts ect.
appParamsFileName = f"_joringels{fext}"
# local directory for storing en/decrpytd files and managing your secrets
encryptDir = unalias_path("~/.ssp")
assert os.path.isdir(encryptDir), f"Not found encryptDir: {encryptDir}"
# path sepeator for path to find your secret inside its source i.e. kdbx
kps_sep = "/"
# default ip to fetch dataSafe from
dataSafeIp = os.environ.get("DATASAFEIP")
dataSavePort = 7000
entriesRoot = "python_venvs"

#### do NOT change params below unless you know what your doing :) ####
def prep_path(checkPath: str, filePrefix=None) -> str:
    checkPath = unalias_path(checkPath)
    checkPath = checkPath if checkPath.endswith(fext) else f"{checkPath}{fext}"
    if os.path.isfile(checkPath):
        return checkPath
    if filePrefix:
        checkPath = f"{filePrefix}_{checkPath}"
    checkPath = os.path.join(encryptDir, checkPath)
    checkPath = checkPath if checkPath.endswith(fext) else f"{checkPath}{fext}"
    return checkPath


def mk_encrypt_path(safeName: str) -> str:
    encrpytPath = os.path.join(encryptDir, f"{safeName}.yml").replace(".yml.yml", ".yml")
    return encrpytPath


# takes the current module and runs function with funcName
settingsPath = os.path.split(__file__)[0]
srcPath = os.path.split(settingsPath)[0]
appBasePath = os.path.split(srcPath)[0]
logDir = os.path.join(srcPath, "logs")
appParamsPath = prep_path(os.path.join(encryptDir, appParamsFileName))
actionImport = "joringels.src.actions"
impStr = f"joringels.src"


# test
testPath = os.path.join(srcPath, "test")
testDataPath = os.path.join(testPath, "data")
# Path function settings
# os seperator correction
os_sep = lambda x: os.path.abspath(x)


def file_or_files(checkPath: str, *args, **kwargs) -> list:
    checkPath = prep_path(checkPath)
    if os.path.isdir(checkPath):
        fileNames = os.listdir(checkPath)
    elif os.path.isfile(checkPath):
        checkPath, fileName = os.path.split(checkPath)
        fileNames = [fileName]
    return checkPath, fileNames


@contextmanager
def temp_safe_rename(*args, safeName: str, prefix: str = "#", **kwargs) -> None:
    """
    temporaryly renames files in .ssp for upload to bypass files
    """
    # rename fileName by adding prefix
    fileName = f"{safeName}.yml"
    currPath = os.path.join(encryptDir, fileName)
    tempPath = os.path.join(encryptDir, f"{prefix}{fileName}")
    try:
        if os.path.exists(currPath):
            os.rename(currPath, tempPath)
        yield
    finally:
        if os.path.exists(tempPath):
            os.rename(tempPath, currPath)


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


try:
    with open(appParamsPath, "r") as f:
        appParams = yaml.safe_load(f)
        appParamsLoaded = True
except FileNotFoundError:
    appParams = {
        "decPrefix": "decrypted_",
        "validator": "text_is_valid",
        "secretsPort": 7000,
    }
    appParamsLoaded = False
