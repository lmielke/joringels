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

    def initialize_apis(self, *args, secrets:dict, safeName:str, **kwargs):
        # import oamailer.actions.send
        self.projectParams = secrets.get(sts.appParamsFileName)
        self.safeName = safeName
        self.apis[safeName] = {k: vs for k, vs in secrets.items() if type(k) == int}
        self._import_api_modules(*args, secrets=secrets, safeName=safeName, **kwargs)

    def _import_api_modules(self, *args, secrets:dict, safeName:str, **kwargs):
        sys.path.append(secrets['apiEndpointDir'])
        self.apiEndpointDir = secrets['apiEndpointDir']
        self.modules[safeName] = self.modules.get(safeName, {})
        for ix, api in self.apis[safeName].copy().items():
            self.modules[safeName][ix] = {'module': import_module(api['import'], self.safeName)}

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
        
