# api_handler.py
import joringels.src.settings as sts
from importlib import import_module
import os, sys
from datetime import datetime as dt
import subprocess

class API:

    def __init__(self, *args, **kwargs):
        self.modules = {}
        self.apis = {}

    def initialize(self, *args, secrets:dict, **kwargs) -> None:
        self.projectParams = secrets.get(sts.appParamsFileName)
        self.apiEndpointDir = secrets['apiEndpointDir']
        self.apis.update(self._initialize_apis(*args, secrets=secrets, **kwargs))
        self.modules.update(self._import_api_modules(*args, secrets=secrets, **kwargs))

    def _initialize_apis(self, *args, secrets:dict, safeName:str, **kwargs) -> None:
        """ fills self.apis with all api entries in secrets (entries with numeric key)
            als calls _import_api_modules fill self.modules with imported modules
            result looks like: {
                                0: {'action': 'send', 'import': 'oamailer.actions.send', ...},
                                1: ...
                                }
        """
        apis = {}
        apis[safeName] = {k: vs for k, vs in secrets.items() if type(k) == int}
        return apis

    def _import_api_modules(self, *args, secrets:dict, safeName:str, **kwargs) -> None:
        """ fills self.modules with imported modules from api import string
            self.modules is used to keep imported modules and avoid import on demand
            result looks like: {
                    0: {'module': <module 'oamailer.actions.send' from ...},
                    1: ...
                    }
        """
        sys.path.append(self.apiEndpointDir)

        modules = {}
        modules[safeName] = modules.get(safeName, {})
        for ix, api in self.apis[safeName].items():
            # import_module without package parameter. Hence provide full path like:
            # oamailer.actions.send
            modules[safeName][ix] = {'module': import_module(api['import'])}
        return modules

    def run_api(self, api, payload, *args, safeName, **kwargs):
        r = getattr(
                    self.modules[safeName][api]['module'],
                    self.apis[safeName][api]['action']
                    )(**payload)
        return r

    def run_api_subprocess(self, api, payload, *args, safeName, **kwargs):
        """
            runs api endpoint as a subprocess
            
        """
        logPath = os.path.join(sts.logDir, f'{safeName}.log')
        params = ['pipenv', 'run', 'python', '-m', 'oamailer', 'send']
        for k, vs in payload.items(): params.extend([f"--{k}", vs])
        with open(logPath, 'a+') as f:
            f.write(f"\n{dt.now()}:\n")
            f.write(f"cwd: {self.apiEndpointDir}\n")
            # f.write(f"missing: {m}")
            try:
                response = 'subprocess out: \n'    
                r = subprocess.run(
                                            params, 
                                            cwd=self.apiEndpointDir,
                                            capture_output=True,
                        )
                response += f"stdout: {r.stdout.decode('latin')}\n"
                response += f"stderr: {r.stderr.decode('latin')}\n"
            except Exception as e:
                f.write(f"subprocess Exception: {e}\n")
            finally:
                f.write(f"finally: {response}\n")
        return {'oamailer': 'done'}
        
