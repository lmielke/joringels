# settings.py

# settings.py
import json, os, sys, time, yaml
from contextlib import contextmanager
from pathlib import Path



def unalias_path(workPath: str) -> str:
    """
    repplaces path aliasse such as . ~ with path text
    """
    if not any([e in workPath for e in ['.', '~', '%']]): return workPath
    workPath = workPath.replace(r"%USERPROFILE%", "~")
    workPath = workPath.replace("~", os.path.expanduser("~"))
    if workPath.startswith(".."):
        workPath = os.path.join(os.path.dirname(os.getcwd()), workPath[3:])
    elif workPath.startswith("."):
        workPath = os.path.join(os.getcwd(), workPath[2:])
    workPath = os.path.normpath(os.path.abspath(workPath))
    return workPath


fext = ".yml"
# kdbx parameters you might want to change
# name of group you create in keeepass that stores dataSafe entries
groupName = "joringels_data_safes"
# keepas/advanced/attachments
# name of params file containing sources an targets for your secrets
safeParamsFileName = f"safe_params{fext}"
# name of general file containing program params such as allowed hosts ect.
appParamsFileName = f"_joringels{fext}"
apiParamsFileName = f"_apis{fext}"
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
def prep_path(workPath: str, filePrefix=None) -> str:
    workPath = unalias_path(workPath)
    workPath = workPath if workPath.endswith(fext) else f"{workPath}{fext}"
    if os.path.isfile(workPath):
        return workPath
    if filePrefix:
        workPath = f"{filePrefix}_{workPath}"
    workPath = os.path.join(encryptDir, workPath)
    workPath = workPath if workPath.endswith(fext) else f"{workPath}{fext}"
    return workPath


def mk_encrypt_path(safeName: str) -> str:
    encrpytPath = os.path.join(encryptDir, f"{safeName.lower()}.yml")
    encrpytPath = encrpytPath.replace(".yml.yml", ".yml")
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


def file_or_files(workPath: str, *args, **kwargs) -> list:
    """ takes a name and checks if its a fileName or dirName
        then returns all files belongin to that file, dir
        i.e. chkey can change one dataSafe key or keys of all dataSafes in dir
    """
    workPath = prep_path(workPath)
    if os.path.isdir(workPath):
        fileNames = os.listdir(workPath)
    elif os.path.isfile(workPath):
        workPath, fileName = os.path.split(workPath)
        fileNames = [fileName]
    return workPath, fileNames


@contextmanager
def temp_safe_rename(*args, safeName: str, prefix: str = "#", **kwargs) -> None:
    """
    temporaryly renames files in .ssp for upload to bypass files
    """
    # rename fileName by adding prefix
    fileName = f"{safeName.lower()}.yml"
    currPath = os.path.join(encryptDir, fileName)
    tempPath = os.path.join(encryptDir, f"{prefix}{fileName}")
    try:
        if os.path.exists(currPath):
            os.rename(currPath, tempPath)
        yield
    finally:
        if os.path.exists(tempPath):
            os.rename(tempPath, currPath)
            time.sleep(1)


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
def temp_unprotected_secret(j: object, entryName: str) -> None:
    """
    Temporarily exposes a secret in .ssp
    """
    fileName = entryName if entryName.endswith(".yml") else f"{entryName}.yml"
    entryPath = os.path.join(encryptDir, fileName)
    entry = j.secrets.get(entryName)
    if entry is None:
        print(f"Entry not found: {entryName}")
    else:
        try:
            with open(entryPath, "w") as f:
                f.write(yaml.dump(entry))
            yield
        finally:
            os.remove(entryPath)


startupParamsPath = os.path.join(srcPath, "resources", appParamsFileName)
try:
    with open(appParamsPath, "r") as f:
        appParams = yaml.safe_load(f)
        appParamsLoaded = True
except FileNotFoundError:
    with open(startupParamsPath, "r") as f:
        appParams = yaml.safe_load(f)
    appParamsLoaded = False


# api endpoints settings


"""
available apps json looks like this
    {
        "oamailer":  [
                        "gitlab.com/yourgitUsername",
                        "~/python_venvs/modules/oamailer"
                    ],
        "kingslanding":  [
                             "gitlab.com/yourgitUsername",
                             "~/python_venvs/kingslanding"
                         ]
    }
"""
available_appsPath = "~/python_venvs/modules/os_setup/droplet/configs/available_apps.json"


# api_endpoint.yml contains the api parameters
# File Example
"""
    projectName: oamailer
    port: 7007

    0:
      import: .actions.send
      action: send
      response: null

"""
api_endpoints_path = lambda projectDir, projectName: os.path.join(
                                                                projectDir,
                                                                projectName,
                                                                'api_endpoints',
                                                                'params.yml'
                                                                )

########### HOST PARMETER ############
# dev computer names
devHost = 'WHILE-'
# serve host or microservice, needed by get_soc.py for host resolve
serveHost = {'joringels': '64.227.67.207'}

def get_api_enpoint_dir(connector, *args, **kwargs):
    with open(unalias_path(available_appsPath), "r") as apps:
        available_apps = json.load(apps)
    app = available_apps.get(connector)
    if not app:
        raise Exception(f"no app found in available_apps.yml named {connector}")
    else:
        return (
                api_endpoints_path(unalias_path(app[1]), connector),
                unalias_path(app[1])
                )