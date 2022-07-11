# jorinde.py
import colorama as color

color.init()
import os, requests, yaml
from copy import deepcopy
import joringels.src.get_soc as soc
import joringels.src.settings as sts


class Jorinde:
    def __init__(self, *args, **kwargs):
        pass

    def _fetch(self, *args, key=False, safeName=False, **kwargs):
        """<br><br>

        *Last update: 2020-11-09*
        ###Hint Secrets
        ___
        ###Asks Joringle Flower for a secret

        ########################### START TEST ###########################
        # INPUTS
        key: testkey
        safeName: TestJoringels
        encryptPath: /python_venvs/packages/joringels/joringels/src/test/test_get.yml

        # FUNCTION
        pyCall: instance.get(**kwargs)
        shellCall: None

        # RETURN
        returns: {'TestJoringels': 'pyCallTestString'}

        ########################### END TEST ###########################

        """
        host, port = soc.host_info(*args, **kwargs)
        resp = requests.get(f"http://{host}:{port}/{safeName}")
        try:
            if resp.status_code == 200:
                secret = yaml.safe_load(resp.text)
            else:
                secret = {"ERROR": resp.text}
        except Exception as e:
            secret = {"ERROR": e}
        return secret

    # def authorized(self, method, *args, **kwargs):
    #     if method == "_unpack_decrypted" and (
    #         soc.get_hostname() not in sts.appParams.get("secureHosts")
    #     ):
    #         print(f"Action not allowed on this host: {soc.get_hostname()}")
    #         return False
    #     else:
    #         return True

    def _unpack_decrypted(self, *args, safeName, **kwargs):
        decPath = sts.prep_path(safeName, "unprotectedload")
        with open(decPath, "r") as f:
            entries = yaml.safe_load(f)
        # save every parameter to a seperate file
        decDir, decFileName = os.path.split(decPath)
        for entry, prs in entries.items():
            if entry == "key":
                continue
            else:
                if not entry.endswith(sts.fext):
                    entry = f"{entry}{sts.fext}"
            with open(os.path.join(decDir, entry), "w") as f:
                f.write(yaml.dump(prs))
        os.remove(decPath)
        msg = f"Saved entries to .ssp, NOTE: entries are unprotected !"
        print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
        return True
