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
fext, eext = ".yml", ".json"
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
decPrefix = ""
validator = "text_is_valid"
#### do NOT change params below unless you know what your doing :) ####

# ****************** MUST NOT CHANGE PARAMS ***********************#
# takes the current module and runs function with funcName
settingsPath = os.path.split(__file__)[0]
srcPath = os.path.split(settingsPath)[0]
appBasePath = os.path.split(srcPath)[0]
logDir = os.path.join(srcPath, "logs")
appParamsPath = prep_path(os.path.join(encryptDir, appParamsFileName))


# test paths and data used for unittesting
testPath = os.path.join(srcPath, "test")
testDataDir = os.path.join(testPath, "data")
testLogDir = os.path.join(testPath, "logs")
# tests use these inputs to create test data for joringels
testKey = "testKey"  # key to enycrypt test data
testDataDict = {"Joringel": "Jorinde"}  # decrypted test data to be encrypted
# encrypted test data, NOTE: decryption using testKey='testKey' results in testDataDict
testDataStr = (
    f"gv2b6OhLiCUbc5OrVrvXVDpvgBzi/Zi05nXsSYD93NA=:tw49vW9rg0v1clTo92lM7w==:"
    f"m66Dwox/axAaUP4JGPUAR6oUi91e9A38VSyep8W46B3PImE7VLddvbAr5qC2A40Dk4f74h"
    f"w+YeBBsAufrMkBHj+MiPiPqSsE7r7tBeb6ezMSzLbaWvMABdiW3blyZmulBKahCptjZ0yM"
    f"a1jjDwVa0SEeMrCW1MTYZViATmJJPZ6ty9s9Y7ZhIm9/7XkljE1DXmqeENS+rX/w5XXSN2"
    f"tQlQ=="
)
cryptonizeDataStr = (
    f"aZwqGLxJ6kfKllpgmUbfm57mksEhJjxhphxPdJC+HrQ=:kAmDCc3JffxxxxP5nG2FyQ==:"
    f"ox2XcWCW9fz84vM7brqdQFisUzV2MaFdepRR7CFuIF4pUjL8Gls1Rcherf3KEbOIDBr7f8"
    f"1GcFJUwNPmPrqkxxLWf84+t9R1ssOnLWgCFqMYxpEpVYuoMxsOXXgIDd+LrYB2m9eGCIr0"
    f"FKP2jZ9m4A/pW1dfNBYlyAmindfCsh93LRsFDijkMR9AVf0lwD+Y6OsPfruqDA9mGHRnNu"
    f"+OjA=="
)
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
