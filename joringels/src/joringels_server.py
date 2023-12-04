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


class JoringelsServer(Joringel):
    """
    JoringelsServer is a WebServer which provides a REST API for the connector
    that has been passed in as an argument. The connector has to exist inside self.secrets
    and the connectors parameters are used to initialize and store and serve the connectors
    package as API.
    """

    sessions = {}

    def __init__(self, *args, clusterName, connector="joringels", host=None, port=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.connector, self.clusterName = connector, clusterName
        self.sessions = {"initial": re.sub(r"([: .])", r"-", str(dt.now()))}
        self.apiHand = ApiHandler(*args, **kwargs)

    @property
    def joringelsParams(self, *args, **kwargs):
        return dict_decrypt(self.secrets)[self.clusterName][sts.cluster_params][
            sts.appParamsFileName
        ]

    def server(self, *args, host: str, port: int, **kwargs):
        """
        starts the http server
        """
        self._digest(*args, **kwargs)
        self._prep_params(*args, **kwargs)
        self._initialize_api_endpoint(*args, **kwargs)
        self._memorize(*args, **kwargs)
        self._serve(*args, **kwargs)

    def _prep_params(self, *args, clusterName: str = None, **kwargs):
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
        # print(f"\n_prep_params: {clusterParams = }")
        if clusterParams.get(sts.apiParamsFileName):
            # this extracts api params from clusterParams and stores a encrypted copy
            # api params are needed to identify and run the api as requested by jorinde
            api = self._handle_integer_keys(clusterParams[sts.apiParamsFileName])
            clusterParams[sts.apiParamsFileName] = api
            # if services are present, they contain serving host and port info
            self.api = dict_encrypt(api)
            # self.host = soc.get_host(api, self.host, *args, **kwargs)
            # self.port = soc.get_port(api, self.port, *args, connector=self.connector, **kwargs)
        # joringels basic runntime params like allowedHosts must be loaded from secrets
        if clusterParams.get(sts.appParamsFileName):
            sts.appParams.update(clusterParams[sts.appParamsFileName])
        self.sessions.update({"serving": re.sub(r"([: .])", r"-", str(dt.now()))})
        return True

    def _initialize_api_endpoint(self, *args, connector, safeName=None, **kwargs):
        """
        calls the api_endpoint module which imports relevant api modules and
        executes them if requested
        joringels itself is not held as api because joringels is the base application
        """
        self.apiHand.initialize(
            *args,
            apis=dict_decrypt(self.api),
            safeName=self.safeName,
            connector=self.connector,
            **kwargs,
        )
        self.secrets["logunittest"] = (
            f"FROM {soc.get_hostname()}.{self.connector.upper()}: "
            + self.apiHand.modules[self.connector]["logunittest"]
        )

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

    def _serve(self, *args, host=None, port=None, **kwargs):
        """
        takes secrets/api params and passes it on to the flower.py http server when
        'jo serve' is called
        flower.py will then handle the http part
        """
        # host = host if host is not None else soc.get_local_ip()
        host = self.joringelsParams.get("mappings").get("host")
        port = self.joringelsParams.get("mappings").get("port")
        self.AF_INET = (host, port)
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
