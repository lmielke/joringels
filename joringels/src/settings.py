# settings.py

# settings.py
import json, os, sys, time, yaml
from contextlib import contextmanager
import joringels.src.get_soc as soc
from joringels.src.helpers import unalias_path as unalias_path
from joringels.src.helpers import prep_path as prep_path
import joringels.src.data as data

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

bridgeIpFirstOctet = "172"
# encryption/decryption helper
decPrefix = ""
validator = "text_is_valid"
#### do NOT change params below unless you know what your doing :) ####

# ****************** MUST NOT CHANGE PARAMS ***********************#
# takes the current module and runs function with funcName
settingsPath = os.path.split(__file__)[0]
srcPath = os.path.split(settingsPath)[0]
appBasePath = os.path.split(srcPath)[0]
dockerPath = os.path.join(appBasePath, "docker")
logDir = os.path.join(srcPath, "logs")
appParamsPath = prep_path(os.path.join(encryptDir, appParamsFileName))


# test paths and data used for unittesting
testPath = os.path.join(srcPath, "test")
testDataDir = os.path.join(testPath, "data")
testLogDir = os.path.join(testPath, "logs")
# tests use these inputs to create test data for joringels
testKeyOuter = "testKeyOuter"  # key to enycrypt test data keys
testKeyInner = "testKeyInner"  # key to enycrypt test data
testDataDict = {"Joringel": "Jorinde"}  # decrypted test data to be encrypted
# dict_encrpyt result of testDataDict using key=testKeyOuter, keyV=testKeyInner
cryptonizeDataStr = (
    f"PM44pt6xgMZGD+/O/nlvwkiEgQVPl93DwaWa5aJ0Ycc=:duEwbtsdUpfkZ80z2y5/Cw==:"
    f"E6HU428/PccO8mPCpKpRrZZs5Miky2D37XlXwgr4d7xvEP6GYfUFXVt89lAo8tGejaKiOF"
    f"yMKWaOSAisRYHKqUSI1pydNaUMFl7OAE+KJZU4MBiV5vjHzaVDCrOrxrE0YRQbzJRw71Lr"
    f"0hm9j/HWuoXOS8wPWGfbzIfZ7QF3ObJL84H8+2n/vwdEO1/yo0eu1gerS2CQc5Ob+tKTtf"
    f"9Icg=="
)

# startupParamsPath = os.path.join(srcPath, "resources", appParamsFileName)
# default ip to fetch dataSafe from
defaultHost = "0.0.0.0"
dockerHostPrefix = "172."
defaultPort = 7000
appParams = data.AppParams()


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
