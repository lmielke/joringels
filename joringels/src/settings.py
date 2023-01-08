# settings.py

# settings.py
import json, os, sys, time, yaml
from contextlib import contextmanager
import joringels.src.get_soc as soc
from joringels.src.helpers import unalias_path as unalias_path
from joringels.src.helpers import prep_path as prep_path

# ****************** MUST CHANGE PARAMS ***********************#
""" 
    You must change the followig parameter according to your 
    individual project setup
"""
########################### START src.sources.kdbx parameters ##########################
# NOTE: see joringels.src.test.data.joringels.kdbx for an example
# kdbx-file.dataSafes
kdbxRootGroup = "python_venvs"
dataSafeGroup = "data_safes"
fext = ".yml"
kps_sep = "/"

# kdbx-file.dataSafes.dataSafe.attachments.safe_params.yml
safeParamsFileName = f"safe_params"

# kdbx.products.product.clusterEntry.attachments.cluster_params.yml
cluster_params = "cluster_params"
allowedClients = "allowedClients"
secureHosts = "secureHosts"
appParamsFileName = f"_joringels"
apiParamsFileName = f"services"
providerHost = "ipv4_address"
# dev computer names
devHost = "WHILE-"
exportDir = unalias_path("~/python_venvs/packages/dockerizer/dockerizer/builds")
########################### END src.sources.kdbx parameters ##########################


# ****************** CAN CHANGE PARAMS ***********************#
########################### START joringels base params ###########################
appName = "joringels"

global encryptDir
encryptDir = unalias_path("~/.ssp")
assert os.path.isdir(encryptDir), f"Not found encryptDir: {encryptDir}"

# path sepeator for path to find your secret inside its source i.e. kdbx
# default ip to fetch dataSafe from
defaultSafeIp = os.environ.get("DATASAFEIP")
defaultHost = "0.0.0.0"
defaultPort = 7000
# encryption/decryption helper
decPrefix = "decrypted_"
validator = "text_is_valid"
#### do NOT change params below unless you know what your doing :) ####

# ****************** MUST NOT CHANGE PARAMS ***********************#
# takes the current module and runs function with funcName
settingsPath = os.path.split(__file__)[0]
srcPath = os.path.split(settingsPath)[0]
appBasePath = os.path.split(srcPath)[0]
logDir = os.path.join(srcPath, "logs")
appParamsPath = prep_path(os.path.join(encryptDir, appParamsFileName))


# test
testPath = os.path.join(srcPath, "test")
testDataDir = os.path.join(testPath, "data")
testLogDir = os.path.join(testPath, "logs")
# Path function settings
# os seperator correction
os_sep = lambda x: os.path.abspath(x)


startupParamsPath = os.path.join(srcPath, "resources", appParamsFileName)
try:
    appParams = {}
    with open(appParamsPath.replace(fext, ".json"), "r") as f:
        appParams.update(yaml.safe_load(f))
except FileNotFoundError:
    appParams[secureHosts] = [soc.get_local_ip()]
    appParams[allowedClients] = [soc.get_local_ip()]
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
available_appsPaths = "~/python_venvs/modules/os_setup/droplet/configs/available_apps.json"


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
    projectDir, projectName, "api_endpoints", "params.yml"
)
