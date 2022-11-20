# settings.py

# settings.py
import json, os, sys, time, yaml
from contextlib import contextmanager
from pathlib import Path
import joringels.src.get_soc as soc



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
# name of group in keeepass that stores entries for products i.e. wobbles
# product entries contain the cluster parameter files.yml
dataSafeGroup = "data_safes"
allowedClients = 'allowedClients'
secureHosts = 'secureHosts'
# keepas/advanced/attachments
# name of params file containing sources an targets for your secrets

# files with specific parameter essential for joringels to work properly
safeParamsFileName = f"safe_params"
appParamsFileName = f"_joringels"
apiParamsFileName = f"services"
providerHost = 'ipv4_address'
# app Name
appName = 'joringels'
# in kdbx each cluster has a entry which contais cluster parameter i.e. init password
cluster_params = 'cluster_params'
# local directory for storing en/decrpytd files and managing your secrets
encryptDir = unalias_path("~/.ssp")
exportDir =  unalias_path("~/docker/.ssp")
assert os.path.isdir(encryptDir), f"Not found encryptDir: {encryptDir}"
# path sepeator for path to find your secret inside its source i.e. kdbx
kps_sep = "/"
# default ip to fetch dataSafe from
dataSafeIp = os.environ.get("DATASAFEIP")
defaultPort = 7000
entriesRoot = 'python_venvs'
decPrefix = 'decrypted_'
validator = 'text_is_valid'
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
    print(f"{workPath = }")
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
            if os.path.exists(currPath): os.remove(currPath)
            time.sleep(.1)
            os.rename(tempPath, currPath)
            time.sleep(.1)


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
def temp_secret(j, *args, secretsFilePath:str, entryName:str, **kwargs) -> None:
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
            if fType == '.json':
                json.dump(secrets, f)
            elif fType == '.yml':
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


startupParamsPath = os.path.join(srcPath, "resources", appParamsFileName)
try:
    appParams = {}
    with open(appParamsPath.replace(fext, '.json'), "r") as f:
        appParams.update(yaml.safe_load(f))
except FileNotFoundError:
    appParams[secureHosts] = [soc.get_ip()]
    appParams[allowedClients] = [soc.get_ip()]
    appParams["port"] = defaultPort


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
available_appsPaths = {
                        "nt": "~/python_venvs/modules/os_setup/droplet/configs/available_apps.json",
                        "posix": "~/os_setup/droplet/configs/available_apps.json",

}


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

def get_api_enpoint_dir(connector, *args, **kwargs):
    with open(unalias_path(available_appsPaths.get(os.name)), "r") as apps:
        available_apps = json.load(apps)
    app = available_apps.get(connector)
    if not app:
        raise Exception(f"no app found in available_apps.yml named {connector}")
    else:
        return (
                api_endpoints_path(unalias_path(app[1]), connector),
                unalias_path(app[1])
                )