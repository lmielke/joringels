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
            -f "/python_venvs/packages/joringels/joringels/src/test/test_get.yml"
            -k testkey
            -v 2
 - shellCall get:
    python -m joringels.src.joringels get -c pyCall -f "/python_venvs/packages/joringels/joringels/src/test/test_get.yml"-k testkey -v 2

## NOTE: -hard to make NON RECOVERABLE changes !

"""

import yaml, os, re
import colorama as color

color.init()
from time import sleep
from getpass import getpass as gp

import joringels.src.settings as sts
import joringels.src.flower as magic
import joringels.src.get_soc as soc
from joringels.src.encryption_handler import Handler as decryptor


class Joringel:
    def __init__(self, *args, safeName, secrets=None, verbose=0, **kwargs):
        self.verbose = verbose
        self.safeName = safeName
        self.encryptionPath = sts.prep_path(self.safeName)
        self.secrets = secrets

    def _chkey(self, *args, key, **kwargs):
        """<br><br>

        *Last update: 2020-11-16*
        ###Change Encryption Key
        ___
        ###Decrypts a file using self.key and Encrypts it using -k newKey

        ########################### START TEST ###########################
        # INPUTS NOTE: currently not tested !!!
        key: newKey
        self.safeName: /python_venvs/packages/joringels/joringels/src/test/test_ch_self_key.txt

        # FUNCTION
        pyCall: instance.chkey(allYes=True, **kwargs)
        shell_Call: python modulePath/joringels.py chkey -f self.safeName -k key -y

        # RETURN
        returns: True

        ########################### END TEST ###########################

        """
        if key is None: key = gp(prompt="Enter old key: ", stream=None)
        encryptPath, fileNames = sts.file_or_files(self.safeName, *args, **kwargs)
        msg = f"Continuing will change all keys for: \t{encryptPath}"
        print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
        for fileName in fileNames:
            print(f"\tfile: {fileName}")
        # keys are changed for all files in fileNames
        if newKey := input("\ntype new key to continue: "):
            if input("re-type new key to continue: ") == newKey:
                print(f"changing self.key: {key} to {newKey}")
                for fileName in fileNames:
                    try:
                        filePath = os.path.join(encryptPath, fileName)
                        with decryptor(filePath, key, *args, **kwargs) as f:
                            f.key = newKey
                    except Exception as e:
                        print(f"ERROR: {e}")
            else:
                print(f"keys not matching:")
        else:
            print(f"not changed because invalid pwd: {newKey}")
        return True

    def _digest(self, *args, key, **kwargs):
        """<br><br>

        *Last update: 2020-11-09*
        ###Read Secrets
        ___
        ###Reads encrypted file and decrypts it after reading

        ########################### START TEST ###########################
        # INPUTS
        key: testkey
        self.safeName: "/python_venvs/packages/joringels/joringels/src/test/test_read.yml"

        # FUNCTION
        pyCall: instance._digest(**kwargs)
        shellCall: None

        # RETURN encypted file, test checks if file can be read
        returns: {'pyCall': 'pyCallTestString'}

        ########################### END TEST ###########################

        """
        with decryptor(self.encryptionPath, key, **kwargs) as h:
            with open(h.decryptPath, 'r') as f:
                self.secrets = yaml.safe_load(f.read())
                return h.encryptPath, self.secrets

    def _serve(self, *args, **kwargs):
        """<br><br>

        *Last update: 2020-11-09*
        ###Serve Secrets
        ___
        ###Opens a webserver as runForever which serves secrets to self.get

        ########################### START TEST ###########################
        # INPUTS
        key: testkey
        encryptPath: "/python_venvs/packages/joringels/joringels/src/test/test_read.yml"

        # FUNCTION
        pyCall: instance._serve(**kwargs)
        shellCall: None

        # RETURN
        returns: pyCallTestString

        ########################### END TEST ###########################

        """
        handler = magic.MagicFlower(self)
        if self.secrets:
            magic.HTTPServer(soc.host_info(*args, **kwargs), handler).serve_forever()
        # myServer.server_close()

    def _update_joringels_appParams(self, *args, **kwargs) -> None:
        if not sts.appParamsLoaded:
            sts.appParams.update(self.secrets.get(sts.appParamsFileName, {}))
            with open(sts.appParamsPath, "w") as f:
                f.write(yaml.dump(sts.appParams))
            sts.appParamsLoaded == True
            del self.secrets[sts.appParamsFileName]


def main(*args, **kwargs):
    j = Joringel(*args, **kwargs)
    return j
