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
from joringels.src.api_handler import API


class Joringel:
    def __init__(self, *args, safeName=None, secrets=None, verbose=0, **kwargs):
        self.verbose = verbose
        self.safeName = safeName if safeName else os.environ.get("DATASAFENAME")
        self.encryptPath = sts.mk_encrypt_path(self.safeName)
        self.secrets = secrets
        self.authorized = False
        self.API = API(*args, **kwargs)


    def _chkey(self, *args, key, newKey=None, **kwargs):
        """<br><br>

        *Last update: 2020-11-16*
        ###Change Encryption Key
        ___
        ###Decrypts a file using self.key and Encrypts it using -k newKey


        """
        # confimr key change authorization
        key = Creds(*args, **kwargs).set("old safeName key: ", *args, **kwargs)
        encryptPath, fileNames = sts.file_or_files(self.safeName, *args, **kwargs)
        msg = f"\tContinuing will change all keys for: \t{encryptPath}"
        print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
        # keys are changed for all files in fileNames
        newKey = Creds(*args, **kwargs).set(
            "new key: ", *args, confirmed=False, key=newKey, **kwargs
        )
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
        if auth_checker.authorize_host():
            self.authorized = True
        else:
            return None, None
        # secrets are decryped and returned
        key = key if key is not None else os.environ.get("DATASAFEKEY")
        with decryptor(self.encryptPath, key=key, **kwargs) as h:
            with open(h.decryptPath, "r") as f:
                self.secrets = yaml.safe_load(f.read())
        self.secrets = {int(k) if type(k) is int else k: vs for k, vs in self.secrets.items()}
        self.secrets[sts.appParamsFileName]["lastUpdate"] = re.sub(r"([: .])", r"-", str(dt.now()))
        sts.appParams.update(self.secrets.get(sts.appParamsFileName, {}))
        return h.encryptPath, self.secrets

    def _memorize(self, *args, safeName:str, secrets:dict, **kwargs):
        # secret might refer to application rest parameters, which is handled by self.API
        if secrets.get('contentType') == 'application/json':
            self.API.initialize(*args, secrets=secrets, safeName=self.safeName, **kwargs)
            self.contentType = secrets.get('contentType')
            self.host = secrets.get('host')
            self.port = secrets.get('port')
        # secrets will be encrypted
        self.secrets = dict_encrypt(dict_values_encrypt(
                                                        secrets,
                                                        os.environ.get("DATAKEY")), 
                                    os.environ.get("DATASAFEKEY"))
        return self.secrets



    def _from_memory(self, entry:str, *args, **kwargs) -> str:
        entry = text_decrypt(entry, os.environ.get("DATASAFEKEY"))
        return dict_encrypt({entry: dict_decrypt(self.secrets).get(entry)})

    def _invoke_application(self, entry:str, safeName:str, *args, **kwargs) -> str:
        entry = dict_values_decrypt(dict_decrypt(entry))
        safeName = text_decrypt(safeName, os.environ.get("DATASAFEKEY"))
        # entry = json.loads(text_decrypt(entry, os.environ.get("DATAKEY")).replace("'", '"'))
        response = self.API.run_api(
                                    entry['api'], entry['payload'], *args, 
                                    safeName=safeName, **kwargs
                                    )
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
        AF_INET = soc.host_info_extended(self, *args, **kwargs)

        handler = magic.MagicFlower(self)
        
        if self.secrets:
            magic.HTTPServer(AF_INET, handler).serve_forever()
        # myServer.server_close()

    def _update_joringels_appParams(self, secrets, *args, **kwargs) -> None:
        sts.appParams.update(secrets.get(sts.appParamsFileName, {}))
        with open(sts.appParamsPath, "w") as f:
            f.write(yaml.dump(sts.appParams))
        sts.appParamsLoaded == True
        # del self.secrets[sts.appParamsFileName]


def main(*args, **kwargs):
    j = Joringel(*args, **kwargs)
    return j
