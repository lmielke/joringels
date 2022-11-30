# jorinde.py
import colorama as color

color.init()
import os, requests, yaml
from copy import deepcopy
import joringels.src.get_soc as soc
import joringels.src.settings as sts
from joringels.src.encryption_dict_handler import (
    text_decrypt,
    text_encrypt,
    dict_decrypt,
    dict_encrypt,
    dict_values_decrypt,
    dict_values_encrypt,
)


class Jorinde:
    def __init__(self, *args, **kwargs):
        pass

    def _fetch(
        self,
        *args,
        connector="joringels",
        entryName=False,
        host=None,
        port=None,
        safeName=None,
        **kwargs,
    ):
        """<br><br>

        *Last update: 2020-11-09*
        ###Hint Secrets
        ___
        ###Asks Joringle Flower for a secrets

        ########################### START TEST ###########################
        # INPUTS
        key: testkey
        entryName: TestJoringels
        encryptPath: ~/python_venvs/packages/joringels/joringels/src/test/test_get.yml

        # FUNCTION
        pyCall: instance.get(**kwargs)
        shellCall: None

        # RETURN
        returns: {'TestJoringels': 'pyCallTestString'}

        ########################### END TEST ###########################

        """
        port = soc.get_port(port=port, connector=connector)
        host = soc.get_host(host=host, connector=connector)
        try:
            if connector != "joringels":
                if not type(entryName) == dict:
                    raise Exception(
                        f"Jorinde._fetch ERROR payloaed must be dictionary: {entryName}"
                    )
                url = f"http://{host}:{port}/{text_encrypt(connector, os.environ.get('DATASAFEKEY'))}"
                payload = dict_encrypt(dict_values_encrypt(entryName))
                # POST request
                resp = requests.post(url, headers={"Content-Type": f"{connector}"}, data=payload)
            else:
                # entryName = str(entryName) if entryName is not None else None
                entry = text_encrypt(entryName, os.environ.get("DATASAFEKEY"))
                url = f"http://{host}:{port}/{entry}"
                # GET request
                resp = requests.get(url, headers={"Content-Type": f"{connector}"})

            # prepare response
            if resp.status_code == 200:
                secrets = dict_values_decrypt(dict_decrypt(resp.text))
            else:
                secrets = f"ERROR {resp.status_code}: {resp.text}"
            status_code = resp.status_code
        except Exception as e:
            try:
                status_code = resp.status_code
            except:
                status_code = "000 pre response EXCEPT"
            secrets = {"Jorinde._fetch ERROR {status_code} host: {host}, port: {port}": e}
        # return result
        if connector == "joringels" and not secrets.get(entryName):
            msg = f"Jorinde._fetch ERROR {status_code} host: {host}, port: {port}, Not found: {entryName}"
            print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
            return None
        elif connector == "joringels":
            return secrets.get(entryName)
        else:
            return secrets

    def _unpack_decrypted(self, *args, safeName=None, **kwargs):
        safeName = safeName if safeName is not None else os.environ.get("DATASAFENAME").lower()
        decPath = sts.prep_path(safeName, "unprotectedload")
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
