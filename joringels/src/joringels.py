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
import joringels.src.helpers as helpers
import joringels.src.flower as magic
import joringels.src.get_soc as soc
from joringels.src.encryption_handler import Handler as decryptor
from joringels.src.encryption_dict_handler import text_decrypt, dict_encrypt, dict_decrypt
from joringels.src.get_creds import Creds
import joringels.src.auth_checker as auth_checker
from joringels.src.api_handler import ApiHandler
from logunittest.settings import get_testlogsdir


class Joringel:
    sessions = {}

    def __init__(self, *args, safeName=None, secrets=None, verbose=0, **kwargs):
        self.sessions = {"initial": re.sub(r"([: .])", r"-", str(dt.now()))}
        self.verbose = verbose
        self.safeName = safeName if safeName else os.environ.get("DATASAFENAME")
        self.encryptPath, self.decryptPath = helpers.mk_encrypt_path(self.safeName)
        self.secrets = secrets
        self.authorized = False
        self.apiHand = ApiHandler(*args, verbose=verbose, **kwargs)
        self.host, self.port = None, None

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
            self.secrets = h.data["encrypted"]
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
            self.secrets = h.data["decrypted"]
        self._prep_params(*args, **kwargs)
        return h.encryptPath, self.secrets

    def _prep_params(self, *args, connector: str = None, clusterName: str = None, **kwargs):
        """
        extracts runntime infos from secrets to be used by api endpoint
        for example host, port and network infos
        clusterParams has these infos under _joringels, services
        """
        if "serving" in self.sessions:
            return False
        clusterName = clusterName if clusterName else "testing"
        if not self.secrets.get(clusterName):
            return False
        # hanle all parameter settings and gettings
        clusterParams = self.secrets[clusterName][sts.cluster_params]
        if clusterParams.get(sts.apiParamsFileName):
            # this extracts api params from clusterParams and stores a encrypted copy
            # api params are needed to identify and run the api as requested by jorinde
            api = self._handle_integer_keys(clusterParams[sts.apiParamsFileName])
            clusterParams[sts.apiParamsFileName] = api
            self.api = dict_encrypt(api)
            # if services are present, they contain serving host and port info
            self.host = soc.get_host(api, *args, connector=connector, **kwargs)
            self.port = soc.get_port(api, *args, connector=connector, **kwargs)
        # joringels basic runntime params like allowedHosts must be loaded from secrets
        if clusterParams.get(sts.appParamsFileName):
            sts.appParams.update(clusterParams[sts.appParamsFileName])
        self.sessions.update({"serving": re.sub(r"([: .])", r"-", str(dt.now()))})
        return True

    def _get_recent_logfile(self, connector, *args, **kwargs):
        """
        This is part of the serve/up strategy and allowes to remotely check
        if upping was successfull and joringels runs without errors by checking
        unittest result logs.
        relies on logunittest to be installed and run before 'jo serve'
        jo fetch -e logunittest -ip hostip
        """
        from logunittest.logunittest import Coverage
        from logunittest.actions import stats

        if connector == sts.appName:
            # get joringels testLogDir
            testLogDir = os.path.join(get_testlogsdir(), sts.appName)
        else:
            # get testLogDir of imported apiModule
            testLogDir = self.apiHand.modules[connector]["testLogDir"]
        # print(f"_get_recent_logfile: {testLogDir = }")
        # get header from latest test logfile
        cov = Coverage(logDir=testLogDir)
        cov.get_stats()
        logResults = f" | {cov.latest[0]} | [{stats.main().split('[')[-1]}"
        return logResults

    def _handle_integer_keys(self, apiParams):
        """
        helper function for api calls
        api endpoint calls are called by providing the relevant api action index
        as an integer. During serialization its converted to string and therefore
        has to be reconverted to int here
        """
        apiParams = {int(k) if str(k).isnumeric() else k: vs for k, vs in apiParams.items()}
        return apiParams

    def _initialize_api_endpoint(
        self, *args, safeName: str, secrets: dict, connector: str, **kwargs
    ):
        """
        calls the api_endpoint module which imports relevant api modules and
        executes them if requested
        joringels itself is not held as api because joringels is the base application
        """
        if connector != "joringels":
            self.apiHand.initialize(
                *args,
                apis=dict_decrypt(self.api),
                safeName=self.safeName,
                connector=connector,
                **kwargs,
            )

    def _memorize(self, *args, secrets: dict, connector: str, **kwargs) -> str:
        """
        when 'jo serve' is called, all secrets have to be saved inside a encrypted
        dictionary
        this takes a decrypted dict and returns the encrypted (memorized version)
        latter all get and post requests read from this dictionary
        """
        # test results are added here to be available after cluster server up
        secrets["logunittest"] = (
            f"FROM {soc.get_hostname()}.{connector.upper()}: "
            + self._get_recent_logfile(connector, *args, **kwargs).split("\n")[0]
        )
        self.secrets = dict_encrypt(secrets)
        return self.secrets

    def _from_memory(self, entry: str, *args, **kwargs) -> str:
        """
        reads data from the above memorized dictionary and returns a single requeted entry
        trigger is a get request posted to flower.py
        encrypted entry [key] is provided by the requesting application
        via get request to optain its value.
        This entry is decrypted and then looked up in secrets.
        If found, the value is selected, encrypted like {entryName, value} and returned.
        """
        entryName = text_decrypt(entry, os.environ.get("DATASAFEKEY"))
        entry = dict_decrypt(self.secrets).get(entryName)
        if entry is None:
            return None
        else:
            return dict_encrypt({entryName: entry})

    def _invoke_application(self, payload: str, connector: str, *args, **kwargs) -> str:
        """
        gets a api index from a post request and passes it on to api_handler.py
        payload: dictionary as encrypted string from request data coming from client
                 containing the api index and api payload, see (Readme.md 2. API CALL)
        connector: requestedItem coming as url extension like domain/requesteItem
        """
        payload = dict_decrypt(payload)
        apiName = text_decrypt(connector, os.environ.get("DATASAFEKEY"))
        # payload = json.loads(text_decrypt(payload, os.environ.get("DATAKEY")).replace("'", '"'))
        response = self.apiHand.run_api(
            payload["api"], payload["payload"], *args, connector=apiName, **kwargs
        )
        if response is None:
            return None
        else:
            return dict_encrypt(response)

    def _serve(self, *args, **kwargs):
        """
        takes secrets/api params and passes it on to the flower.py http server when
        'jo serve' is called
        flower.py will then handle the http part
        """
        self.AF_INET = (self.host, self.port)
        handler = magic.MagicFlower(self)
        if self.secrets:
            self.sessions[self.safeName] = self.AF_INET
            if self.verbose:
                print(f"Joringels._serve: {self.sessions = }")
            try:
                magic.HTTPServer(self.AF_INET, handler).serve_forever()
            except OSError as e:
                msg = f"Joringels._serve: {self.AF_INET} with {e}"
                print(f"{RED}{msg}{COL_RM}")
                raise
            except TypeError as e:
                msg = f"Joringels._serve: {self.AF_INET} with {e}"
                print(f"{RED}{msg}{COL_RM}")
                raise


def main(*args, **kwargs):
    j = Joringel(*args, **kwargs)
    return j
