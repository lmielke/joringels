"""""
##################### joringels.Joringel class documentation #####################
SERVER side handler which manages:
joringels mostly serves as an agent for the overall secrets/api handling
NOTE: A machine can act as a server and a client simultaneously
uses imported modules to run funcitons like
    - setting joringels runntime parameters
    - getting secrets from defined sources
    - getting and setting api endpoint parameter
    - launching the WebServer to serve secrets and/or api entpoint data
"""

import os, re
from datetime import datetime as dt

# colors for printing
import colorama as color

color.init()
COL_RM = color.Style.RESET_ALL
YELLOW = color.Fore.YELLOW
GREEN = color.Fore.GREEN
RED = color.Fore.RED

import joringels.src.settings as sts
import joringels.src.get_soc as soc
import joringels.src.helpers as helpers
from joringels.src.encryption_handler import Handler as decryptor
from joringels.src.encryption_dict_handler import text_decrypt, dict_encrypt, dict_decrypt
from joringels.src.get_creds import Creds
import joringels.src.auth_checker as auth_checker
from logunittest.settings import get_testlogsdir


class Joringel:
    def __init__(self, *args, safeName=None, secrets=None, verbose=0, **kwargs):
        self.verbose = verbose
        self.safeName = safeName if safeName else os.environ.get("DATASAFENAME")
        self.encryptPath, self.decryptPath = helpers.mk_encrypt_path(self.safeName)
        self.secrets = secrets
        self.authorized = False

    def _get_pwd(self, *args, key, keyV, newKey=None, newKeyV=None, **kwargs):
        """
        changes the key of all encrypted files within the provided
        directory
        this assumes, that all files use the same encryption + pwd
        """
        # confim key change authorization
        # keys for dict_keys
        key = Creds(uName=self.safeName, kName="key").set(key=key)
        newKey = Creds(uName=self.safeName, kName="newKey").set(key=newKey, confirmed=0)
        # keys for dict_values_encrypt
        keyV = Creds(uName=self.safeName, kName="keyV").set(key=keyV)
        newKeyV = Creds(uName=self.safeName, kName="newKeyV").set(key=newKeyV, confirmed=0)
        return {"key": key, "keyV": keyV, "newKey": newKey, "newKeyV": newKeyV}

    def chkey(self, *args, **kwargs):
        kwargs.update(self._get_pwd(*args, **kwargs))
        self._chkey(*args, **kwargs)

    def _chkey(self, *args, **kwargs):
        print(f"{GREEN}Changing keys for: {self.encryptPath}{COL_RM}")
        encryptPaths = helpers.data_safe_files(*args, **kwargs)
        for encryptPath in encryptPaths:
            try:
                with decryptor(encryptPath, *args, **kwargs) as f:
                    f.change_key(*args, **kwargs)
                print(f"{GREEN}\t{f'Key changed for: {encryptPath}'}{COL_RM}")
            except Exception as e:
                print(f"{RED}{f'CHKEY ERROR: {e}'}{COL_RM}")
                exit()
        return True

    def create(self, *args, key: str = None, keyV: str = None, **kwargs) -> None:
        with decryptor(*args, key=key, keyV=keyV, **kwargs) as h:
            self.secrets = self.prep_cluster_params(h.data["decrypted"], *args, **kwargs)
        return self.secrets

    def _digest(self, *args, key: str = None, keyV: str = None, **kwargs) -> tuple[str, dict]:
        """
        gets the decrypted content from a encrypted file and returns it
        because self.secrets also contains runntime information for joringels
        some of those parameters are added here as well
        """
        if not auth_checker.authorize_host():
            return None, None
        self.authorized = True
        # secrets will decryped and returned
        # key = key if key is not None else os.environ.get("DATASAFEKEY")
        with decryptor(self.encryptPath, key=key, keyV=keyV) as h:
            self.secrets = self.prep_cluster_params(h.data["decrypted"], *args, **kwargs)
        return h.encryptPath, self.secrets

    def prep_cluster_params(self, secrets, *args, clusterName=None, connector=None, **kwargs):
        """
        cluster params are needed to identify the relevant available APIs as well as their
        corresponding ip_address and ports.
        allowedClients and secureHosts are changed in self.secrets in place
        mappings are added like self.secrets['mappings']
        """
        connector = sts.appName if connector is None else connector
        clusterName = clusterName if clusterName is not None else self.get_cluster_name(secrets)
        clusterParams = secrets[clusterName][sts.cluster_params]
        joringelsParams = clusterParams[sts.appParamsFileName]
        # secureHosts and allowed Clients are populated with all cluster ips and ports
        # mappings are colleced for fast readout during select (host, port)
        secureHosts, allowedClients, mappings = [], [], dict()
        for k, vs in clusterParams.get("services").items():
            ip_address = vs["networks"]["illuminati"]["ipv4_address"]
            allowedClients.append(ip_address)
            mappings[k] = {
                "ip_address": ip_address,
                "ports": [int(p) for p in vs.get("ports")[0].split(":")],
            }
            allowedClients.append(soc.get_local_ip())
            allowedClients.append(soc.get_hostname())
            secureHosts.append(soc.get_local_ip())
            secureHosts.append(soc.get_hostname())
        secureHosts.append(os.environ.get("NODEMASTERIP"))
        allowedClients.append(os.environ.get("NODEMASTERIP"))
        joringelsParams["allowedClients"] = list(set(allowedClients))
        joringelsParams["secureHosts"] = list(set(secureHosts))
        mappings["port"] = mappings[connector]["ports"][1]
        mappings["host"] = soc.get_local_ip()
        joringelsParams["mappings"] = mappings
        sts.appParams["mappings"] = mappings
        return secrets

    def get_cluster_name(self, d, current_key=None):
        if isinstance(d, dict):
            for key, value in d.items():
                if key == sts.cluster_params:
                    return current_key
                elif isinstance(value, dict):
                    result = self.get_cluster_name(value, current_key=key)
                    if result is not None:
                        return result
        return None

    def _handle_integer_keys(self, apiParams):
        """
        helper function for api calls
        api endpoint calls are called by providing the relevant api action index
        as an integer. During serialization its converted to string and therefore
        has to be reconverted to int here
        """
        apiParams = {int(k) if str(k).isnumeric() else k: vs for k, vs in apiParams.items()}
        return apiParams

    def _memorize(self, *args, **kwargs) -> str:
        """
        when 'jo serve' is called, all secrets have to be saved inside a encrypted
        dictionary
        this takes a decrypted dict and returns the encrypted (memorized version)
        latter all get and post requests read from this dictionary
        """
        # test results are added here to be available after cluster server up

        self.secrets = dict_encrypt(self.secrets)
        return self.secrets


def main(*args, **kwargs):
    j = Joringel(*args, **kwargs)
    return j
