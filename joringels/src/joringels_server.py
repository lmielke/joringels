# flower.py
import json, os, re

# colors for printing
import colorama as color

color.init()
COL_RM = color.Style.RESET_ALL
YELLOW = color.Fore.YELLOW
GREEN = color.Fore.GREEN
RED = color.Fore.RED

from http.server import HTTPServer
import joringels.src.settings as sts
import joringels.src.get_soc as soc
from datetime import datetime as dt
from joringels.src.encryption_dict_handler import text_decrypt, dict_encrypt, dict_decrypt
import joringels.src.flower as magic
from joringels.src.joringels import Joringel
from joringels.src.api_handler import ApiHandler
import joringels.src.data as data


class JoringelsServer(Joringel):
    """
    JoringelsServer is a WebServer which provides a REST API for the connector
    that has been passed in as an argument. The connector has to exist inside self.secrets
    and the connectors parameters are used to initialize and store and serve the connectors
    package as API.
    """

    sessions = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sessions = {"initial": re.sub(r"([: .])", r"-", str(dt.now()))}

    def server(self, *args, **kwargs):
        """
        starts the http server
        """
        self.prep_params(*args, **kwargs)
        self._initialize_api_endpoint(*args, **kwargs)
        self._memorize(*args, **kwargs)
        # self._serve(*args, **kwargs)

    def prep_params(self, *args, **kwargs):
        self._digest(*args, **kwargs)
        self._prep_api_params(*args, **kwargs)

    def _prep_api_params(self, *args, clusterName: str, connector: str, **kwargs):
        """
        extracts runntime infos from secrets to be used by api endpoint
        for example host, port and network infos
        """
        if "serving" in self.sessions:
            return False
        # clusterName = clusterName if clusterName else "testing"
        elif not self.secrets.get(clusterName):
            return False
        # hanle all parameter settings and gettings
        # joringels basic runntime params like allowedHosts must be loaded from secrets
        clParams = self.secrets[clusterName][sts.cluster_params]["services"][connector]
        self.apiParams = data.apiParams(
            connector=connector,
            api={int(k): vs for k, vs in clParams.items() if str(k).isnumeric()},
        )
        self.sessions.update({"serving": re.sub(r"([: .])", r"-", str(dt.now()))})
        return True

    def _initialize_api_endpoint(self, *args, connector, **kwargs):
        """
        calls the api_endpoint module which imports relevant api modules and
        executes them if requested
        joringels itself is not held as api because joringels is the base application
        """
        self.apiHand = ApiHandler(*args, connector=connector, **kwargs)
        self.apiHand._import_api_modules(*args, apis=self.apiParams.api, **kwargs)
        self.secrets["logunittest"] = (
            f"FROM {soc.get_hostname()}.{connector.upper()}: "
            f" {self.apiHand.modules['logunittest']}"
        )

    def _invoke_application(self, data: str, connector: str, *args, **kwargs) -> str:
        """
        gets a api index from a post request and passes it on to api_handler.py
        data: dictionary as encrypted string from request data coming from client
                 containing the api index and api data, see (Readme.md 2. API CALL)
        connector: requestedItem coming as url extension like domain/requesteItem
        """
        data = dict_decrypt(data)
        apiName = text_decrypt(connector, os.environ.get("DATASAFEKEY"))
        # data = json.loads(text_decrypt(data, os.environ.get("DATAKEY")).replace("'", '"'))
        response = self.run_api(*args, connector=apiName, **data, **kwargs)
        if response is None:
            return None
        else:
            return dict_encrypt(response)

    def run_api(self, *args, **kwargs):
        return self.apiHand.run_api(*args, **kwargs)

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

    def serve(self, *args, host=None, port=None, **kwargs):
        """
        takes secrets/api params and passes it on to the flower.py http server when
        'jo serve' is called
        flower.py will then handle the http part
        """
        # host = host if host is not None else soc.get_local_ip()
        host = sts.clParams.host
        port = sts.clParams.port
        self.AF_INET = (host, port)
        handler = magic.MagicFlower(self)
        if self.secrets:
            self.sessions[self.dataSafe.safeName] = self.AF_INET
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
