# get_secrets.py

from datetime import datetime as dt
import os, re, yaml, json
import colorama as color
color.init()

import joringels.src.settings as sts
from joringels.src.actions import fetch

# :)L0veMi11i0n$
class Applcation:
    def __init__(self, action, *args, verbose=0, key=None, **kwargs):
        self.verbose = verbose
        self.secrets = {}
        self.encrpytKey = os.environ.get('DATASAFEKEY')

    def get_api_enpoint_path(self, safeName, *args, **kwargs):
        with open(sts.unalias_path(sts.available_appsPath), "r") as apps:
            available_apps = json.load(apps)
        app = available_apps.get(safeName)
        if not app:
            raise Exception(f"no app found in available_apps.yml named {safeName}")
        else:
            return (
                    sts.api_endpoints_path(sts.unalias_path(app[1]), safeName),
                    sts.unalias_path(app[1])
                    )

    def get_api_params(self, apiParamsPath, *args, **kwargs):
        with open(apiParamsPath, 'r') as f: 
            self.secrets = yaml.safe_load(f)
        

    def load(self, *args, connector, **kwargs):
        apiParamsPath, apiEndpointDir = self.get_api_enpoint_path(*args, **kwargs)
        self.get_api_params(apiParamsPath, *args, **kwargs)
        self.add_api_enpoint_params(apiEndpointDir, *args, **kwargs)
        self._write_joringels_params(*args, **kwargs)


    def _write_joringels_params(self, *args, safeName, filePrefix=None, **kwargs):
        filePrefix = filePrefix if filePrefix else sts.decPrefix
        fileName = f"{filePrefix}{safeName}.yml"
        filePath = sts.prep_path(os.path.join(sts.encryptDir, fileName))

        # file extension is .yml
        with open(filePath, "w") as f:
            f.write(yaml.dump(self.secrets))

    def add_api_enpoint_params(self, apiEndpointDir, *args, safeName, **kwargs):
        _joringels = fetch.alloc(entryName='_joringels.yml', retain=True)
        _joringels['DATASAFENAME'] = safeName
        _joringels['port'] = self.secrets.get('port')
        _joringels['application'] = safeName
        del _joringels['kPath']
        self.secrets[sts.appParamsFileName] = _joringels
        self.secrets['apiEndpointDir'] = apiEndpointDir

def main(action=None, *args, **kwargs):
    inst = Applcation(action, *args, **kwargs)
    if action is None:
        return inst
    else:
        return getattr(inst, action)(*args, **kwargs)


if __name__ == "__main__":
    import joringels.src.arguments as arguments

    kwargs = arguments.mk_args().__dict__
    keepass = main(**kwargs)
