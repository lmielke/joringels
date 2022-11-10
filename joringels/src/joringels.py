"""""
##################### joringels_code.Joringel class documentation #####################

<img src="https://drive.google.com/uc?id=1C8LBRduuHTgN8tWDqna_eH5lvqhTUQR4" alt="me_happy" class="plain" height="200px" width="310px">

## B: Module Code of (Runner, Code):
Contains the Joringel Class and code

## Available shell cmds (only these can be called from shell using argparse params)
### Table cmds:
|Nr  | action   | description                  | examples                                    |
|---:|:---------|:-----------------------------|:--------------------------------------------|
| 2  | chkey    | changes self.key to newKey   | info [-hard]                                |
| 5  | _digest   | reads/reomves a secrets file | _serve -f  -k testkey |
| 9  | _serve    | runs MagicFlower             |                         |
| 10 | upload   | upload to server             | show -n globals [-o pipe.table.T]           |
| 10 | info     | short help                   | show -n globals [-o pipe.table.T]           |
### End cmds
## CALL: python joringels.py action -param ParamValue or psn action -param ParamValue
## NOTE: if no key is provided, default key will be used see keypass 

## main self are specified by globals.yml, users.yml, locals.yml (<-- Note precedence order)
    - NOTE: precedence order means, that latter exist file vars overwrites earlier file vars
    - ps: contains aggregated values with overwrite order: globals, users, locals
    - self.: all ps vars can be accessed as self. variables if you know their names
    - self.globals, self.users, self.locals contain current variable state as in .yml files

Run examples: Note: remove linebreaks and spaces when copying
MAIN DIR: python $hot/modulePath/...   <-- for more examples check dockstrings TEST section
 - pyCall show:            joringels.Joringel(__file__, **kwargs).show(**kwargs)
 - shellCall get_settings: joringels.py get_settings -n globals -o pipe.table.T
 - shellCall _serve: python ./joringels/src/joringels.py _serve 
            -c pyCall 
            -f "~/python_venvs/packages/joringels/joringels/src/test/test_get.yml"
            -k testkey
            -v 2
 - shellCall get:
    python -m joringels.src.joringels get -c pyCall -f "~/python_venvs/packages/joringels/joringels/src/test/test_get.yml"-k testkey -v 2

## NOTE: -hard to make NON RECOVERABLE changes !

"""

import yaml, os, re, sys, time
from datetime import datetime as dt
import colorama as color

color.init()


import joringels.src.settings as sts
import joringels.src.flower as magic
import joringels.src.get_soc as soc
from joringels.src.encryption_handler import Handler as decryptor
from joringels.src.encryption_dict_handler import text_decrypt, text_encrypt, dict_encrypt, dict_decrypt, dict_values_decrypt, dict_values_encrypt
from joringels.src.get_creds import Creds
import joringels.src.auth_checker as auth_checker
from joringels.src.api_handler import ApiHandler


class Joringel:
    sessions = {}

    def __init__(self, *args, safeName=None, secrets=None, verbose=0, **kwargs):
        self.joringels_runntime = {'initial': re.sub(r"([: .])", r"-" , str(dt.now()))}
        self.verbose = verbose
        self.safeName = safeName if safeName else os.environ.get("DATASAFENAME")
        self.encryptPath = sts.mk_encrypt_path(self.safeName)
        self.secrets = secrets
        self.authorized = False
        self.apiHand = ApiHandler(*args, verbose=verbose, **kwargs)
        self.host, self.port = None, None

    def _chkey(self, *args, key, newKey, allYes=None, **kwargs):
        """<br><br>

        *Last update: 2020-11-16*
        ###Change Encryption Key
        ___
        ###Decrypts a file using self.key and Encrypts it using -k newKey


        """
        # confimr key change authorization
        key = Creds(*args, **kwargs).set(f"old {self.safeName} key: ", *args, key=key, **kwargs)
        encryptPath, fileNames = sts.file_or_files(self.safeName, *args, **kwargs)
        if len(fileNames) >= 2 and allYes is None:
            msg = f"Confirm key changes for {fileNames} [Y or ENTER]: "
            if not input(f"{color.Fore.YELLOW}{msg}{color.Style.RESET_ALL}").upper() == 'Y':
                msg = f"Key change interrupted by user intervention. "
                print(f"{color.Fore.GREEN}{msg}{color.Style.RESET_ALL}")
                exit()
        # keys are changed for all files in fileNames
        newKey = Creds(*args, **kwargs).set(
            "new key: ", *args, confirmed=False, key=newKey, **kwargs )
        # changing keys
        for fileName in fileNames:
            try:
                filePath = os.path.join(encryptPath, fileName)
                with decryptor(filePath, *args, key=key, **kwargs) as f:
                    f.key = newKey
                msg = f"\tKey changed for: {fileName}"
                print(f"{color.Fore.GREEN}{msg}{color.Style.RESET_ALL}")
            except Exception as e:
                msg = f"ERROR: {e}"
                print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
                exit()
        return True

    def _digest(self, *args, key=None, **kwargs):
        """<br><br>

        *Last update: 2020-11-09*
        ###Read Secrets
        ___
        ###Reads encrypted file and decrypts it after reading

        """
        if not auth_checker.authorize_host(): return None, None
        self.authorized = True
        # secrets will decryped and returned
        key = key if key is not None else os.environ.get("DATASAFEKEY")
        with decryptor(self.encryptPath, key=key, **kwargs) as h:
            with open(h.decryptPath, "r") as f:
                self.secrets = yaml.safe_load(f.read())
        self._prep_secrets(*args, **kwargs)
        return h.encryptPath, self.secrets

    def check_runntime(self, *args, **kwargs) -> None:
        """
            checks the runntime state and sets it to False if its undefined (at serve startup)
            some behavior differs depending on runntime state
            i.e. joringels runntime parameters are only set at startup
        """
        os.environ['joringels_runntime'] = os.environ.get('joringels_runntime', 'initial')
        self.joringels_runntime = os.environ['joringels_runntime']

    def _prep_secrets(self, *args, connector:str=None, clusterName:str=None, **kwargs):
        if 'running' in self.joringels_runntime: return True
        clusterName = clusterName if clusterName else 'dev'
        # hanle all parameter settings and gettings
        if self.secrets.get(clusterName):
            clusterParams = self.secrets[clusterName][sts.cluster_params]
        else:
            return False
        # if provided connector is present in secrets, then those paams are used latter
        if clusterParams.get(sts.apiParamsFileName):
            apiParams = self._handle_integer_keys(clusterParams[sts.apiParamsFileName])
            clusterParams[sts.apiParamsFileName] = apiParams
            self.host, self.port = soc.host_info_extended(apiParams, *args, 
                                                        connector=connector, **kwargs)
            self.api = dict_encrypt(dict_values_encrypt(
                                                        apiParams,
                                                        os.environ.get("DATAKEY")), 
                                    os.environ.get("DATASAFEKEY"))
        # joringels basic runntime params like allowedHosts must be loaded from secrets
        if clusterParams.get(sts.appParamsFileName):
            sts.appParams.update(clusterParams[sts.appParamsFileName])
        self.joringels_runntime.update({'running': re.sub(r"([: .])", r"-" , str(dt.now()))})
        return True

    def _handle_integer_keys(self, apiParams):
        apiParams = {int(k) if type(k) is int else k: vs for k, vs in apiParams.items()}
        return apiParams

    def _initialize_api_endpoint(self, *args, safeName:str, secrets:dict, connector:str, **kwargs):
        if connector != 'joringels':
            self.apiHand.initialize(
                                    *args, 
                                    apis=dict_values_decrypt(dict_decrypt(self.api)), 
                                    safeName=self.safeName,
                                    connector=connector,
                                    **kwargs
                            )
    
    def _memorize(self, *args, safeName:str, secrets:dict, connector:str, **kwargs):
        # secrets will be encrypted
        self.secrets = dict_encrypt(dict_values_encrypt(
                                                        secrets,
                                                        os.environ.get("DATAKEY")), 
                                    os.environ.get("DATASAFEKEY"))
        return self.secrets

    def _from_memory(self, entry:str, *args, **kwargs) -> str:
        entry = text_decrypt(entry, os.environ.get("DATASAFEKEY"))
        found = dict_decrypt(self.secrets).get(entry)
        if found is None:
            return None
        else:
            return dict_encrypt({entry: found})


    def _invoke_application(self, entry:str, apiName:str, *args, **kwargs) -> str:
        """
            entry: request data coming from the client containing the
                    api index and api payload
            safeName: requestedItem coming as url extension like domain/requesteItem
        """
        entry = dict_values_decrypt(dict_decrypt(entry))
        connector = text_decrypt(apiName, os.environ.get("DATASAFEKEY"))
        # entry = json.loads(text_decrypt(entry, os.environ.get("DATAKEY")).replace("'", '"'))
        response = self.apiHand.run_api(
                                    entry['api'], entry['payload'], *args, 
                                    connector=connector, **kwargs
                                    )
        if response is None:
            return None
        else:
            return dict_encrypt(dict_values_encrypt(response))

    def clean(self, encrypted, *args, **kwargs):
        decrypted = {}
        for k, vals in encrypted.items():
            if vals is None: continue
            decrypted[k] = yaml.safe_load(text_decrypt(vals, os.environ.get("DATAKEY")))
        return decrypted

    def _serve(self, *args, **kwargs):
        """<br><br>

        *Last update: 2020-11-09*
        ###Serve Secrets
        ___
        ###Opens a webserver as runForever which serves secrets to self.get

        ########################### START TEST ###########################
        # INPUTS
        key: testkey
        encryptPath: "~/python_venvs/packages/joringels/joringels/src/test/test_read.yml"

        # FUNCTION
        pyCall: instance._serve(**kwargs)
        shellCall: None

        # RETURN
        returns: pyCallTestString

        ########################### END TEST ###########################

        """
        self.AF_INET = (self.host, self.port)

        handler = magic.MagicFlower(self)
        if self.secrets:
            self.sessions[self.safeName] = self.AF_INET
            if self.verbose: print(f"Joringels._serve: {self.sessions = }")
            magic.HTTPServer(self.AF_INET, handler).serve_forever()
        # myServer.server_close()

    def _update_joringels_appParams(self, secrets, *args, **kwargs) -> None:
        sts.appParams.update(secrets.get(sts.appParamsFileName, {}))
        with open(sts.appParamsPath.replace(sts.fext, '.json'), 'w+') as f:
            json.dump(sts.appParams, f)

def main(*args, **kwargs):
    j = Joringel(*args, **kwargs)
    return j
