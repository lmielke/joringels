# jorinde.py
"""
    client side handler of self.secrets and requests
    i.e. if a secret is requested jorinde creates the get/post requests and
    handles the server self.response
"""
import colorama as color

color.init()
import os, requests, yaml
import joringels.src.get_soc as soc
import joringels.src.settings as sts
import joringels.src.helpers as helpers
from joringels.src.encryption_dict_handler import text_encrypt, dict_decrypt, dict_encrypt
from joringels.src.actions import fetch


class Jorinde:
    def __init__(self, *args, host=None, port=None, **kwargs):
        self.tgtHost = sts.clParams.host
        self.tgtPort = sts.clParams.port if port is None else port
        self.response = None
        self.secrets = None

    def get_service_params(self, *args, connector, entryName=None, host=None, port=None, **kwargs):
        self.serviceParams = fetch.main(
            *args,
            entryName=f"clParams",
            host=sts.dataSafe.safeIp,
            port=sts.dataSafe.safePort,
            **kwargs,
        )

    def mk_targets(self, *args, connector, **kwargs):
        if os.name == "nt":
            self.tgtHost = soc.get_local_ip()
        else:
            self.tgtHost = self.serviceParams["services"].get(connector).get("host")
        self.tgtPort = self.serviceParams["services"].get(connector).get("port")

    def _fetch(self, *args, **kwargs):
        """
        makes a get/post request to server and returns the self.response
        """
        kwargs["connector"] = kwargs.get("connector", "joringels")
        try:
            if kwargs.get("connector") == "joringels":
                self.get_request(*args, **kwargs)
            else:
                self.get_service_params(*args, **kwargs)
                self.mk_targets(*args, **kwargs)
                self.post_request(*args, **kwargs)
            self.validate_response(*args, **kwargs)
        except Exception as e:
            try:
                statusCode = self.response.status_code
            except:
                statusCode = "000 pre self.response EXCEPT"
            finally:
                self.secrets = f"Jorinde._fetch ERROR status: {statusCode}, host: {self.tgtHost}, port: {self.tgtPort}: {e}"
                print(f"{color.Fore.RED}{self.secrets}{color.Style.RESET_ALL}")
        return self.clean_response(*args, **kwargs)

    def post_request(self, *args, entryName, connector: str, **kwargs):
        """
        sends an encrypted post request to the specified host/port server
        """
        entry = text_encrypt(connector, os.environ.get("DATASAFEKEY"))
        url = f"http://{self.tgtHost}:{self.tgtPort}/{entry}"
        if not type(entryName) == dict:
            raise Exception(f"Jorinde.post_request ERROR must be dictionary: {entryName}")
        payload = dict_encrypt(entryName)
        self.response = requests.post(url, headers={"Content-Type": f"{connector}"}, data=payload)

    def get_request(self, *args, entryName, connector, **kwargs):
        entry = text_encrypt(entryName, os.environ.get("DATASAFEKEY"))
        url = f"http://{self.tgtHost}:{self.tgtPort}/{entry}"
        self.response = requests.get(url, headers={"Content-Type": f"{connector}"})

    def validate_response(self, *args, connector, **kwargs):
        # prepare self.response
        if self.response.status_code == 200:
            self.secrets = dict_decrypt(self.response.text)
        else:
            self.secrets = f"ERROR {self.response.status_code}: {self.response.text}"

    def clean_response(self, *args, entryName, connector, **kwargs):
        if type(self.secrets) == str:
            msg = f"Jorinde._fetch ERROR, {connector}: {self.tgtHost}, self.tgtPort: {self.tgtPort}, Not found: {entryName}"
            print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
            return None
        elif connector == "joringels" and not self.secrets.get(entryName):
            msg = f"Jorinde._fetch ERROR, {connector}: {self.tgtHost}, self.tgtPort: {self.tgtPort}, Not found: {entryName}"
            print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
            return None
        elif connector == "joringels":
            return self.secrets.get(entryName)
        else:
            return self.secrets

    def _unpack_decrypted(self, *args, safeName=None, **kwargs):
        safeName = safeName if safeName is not None else os.environ.get("DATASAFENAME").lower()
        decPath = helpers.prep_path(safeName, "unprotectedload")
        with open(decPath, "r") as f:
            entries = yaml.safe_load(f)
        # save every parameter to a seperate file
        decDir, decFileName = os.path.split(decPath)
        for entryName, prs in entries.items():
            if entryName == "key":
                continue
            else:
                if not entryName.endswith(sts.fext):
                    entryName = f"{entryName}{sts.fext}"
            with open(os.path.join(decDir, entryName), "w") as f:
                f.write(yaml.dump(prs))
        os.remove(decPath)
        msg = f"Jorinde._fetch ERROR, Saved entries to .ssp, NOTE: entries are unprotected !"
        print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
        return True
