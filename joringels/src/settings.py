# settings.py

# settings.py
import os, sys, yaml
from contextlib import contextmanager
from pathlib import Path



# keepass parameters you might want to change
# name of group in keeepass that stores data_safes entries
safeLocation = "joringels_data_safes"
# keepas/advanced/attachments
# name of params file containing sources an targets for your secrets
safeParamsFileName = "safe_params.yml"
# name of general file containing program params such as allowed hosts ect.
appParamsFileName = "application.yml"
# local directory for storing en/decrpytd files and managing your secrets
encryptDir = "~/.ssp"
# path sepeator for path to find your secret inside its source i.e. keepass
kps_sep = "/"



#### do NOT change params below unless you know what your doing :) ####
def prep_path(checkPath: str, filePrefix=None) -> str:
    checkPath = checkPath.replace("~", os.path.expanduser("~"))
    checkPath = checkPath if checkPath.endswith(".yml") else f"{checkPath}.yml"
    if os.path.isfile(checkPath):
        return checkPath
    if checkPath.startswith("."):
        checkPath = os.path.join(os.getcwd(), checkPath[2:]).replace("/", os.sep)
    if filePrefix:
        checkPath = f"{filePrefix}_{checkPath}"
    checkPath = os.path.join(encryptDir, checkPath)
    checkPath = checkPath.replace("~", os.path.expanduser("~"))
    checkPath = checkPath if checkPath.endswith(".yml") else f"{checkPath}.yml"
    return checkPath


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
    }
    appParamsLoaded = False
