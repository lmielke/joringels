# api_handler.py
import joringels.src.settings as sts
import joringels.src.helpers as helpers
from importlib import import_module
import os, sys
from datetime import datetime as dt
import subprocess


class ApiHandler:
    def __init__(self, *args, verbose=0, **kwargs):
        self.verbose = verbose
        self.modules = {}
        self.apis = {}

    def initialize(self, *args, apis: dict, **kwargs) -> None:
        if self.verbose:
            print(f"\njoringels.api_handler.initialize: {apis = }\n")
        self.apis.update(self._initialize_apis(*args, apis=apis, **kwargs))
        self.modules.update(self._import_api_modules(*args, apis=apis, **kwargs))

    def _initialize_apis(self, *args, apis: dict, connector: str, **kwargs) -> None:
        """fills self.apis with all api entries in apiActions (entries with numeric key)
        als calls _import_api_modules fill self.modules with imported modules
        result looks like: {
                            0: {'action': 'send', 'import': 'oamailer.actions.send', ...},
                            1: ...
                            }
        """
        apiActions = apis.get(connector)
        actions = {}
        actions[connector] = {int(k): vs for k, vs in apiActions.items() if k.isnumeric()}
        return actions

    def _import_api_modules(self, *args, connector: str, **kwargs) -> None:
        """fills self.modules with imported modules from api import string
        self.modules is used to keep imported modules and avoid import on demand
        result looks like: {
                0: {'module': <module 'oamailer.actions.send' from ...},
                1: ...
                }
        """
        self.apiEndpointDir = helpers.get_api_enpoint_dir(connector)
        sys.path.append(self.apiEndpointDir)
        modules = {connector: {}}
        # modules[connector] = modules.get(connector, {})
        for ix, api in self.apis[connector].items():
            # import_module without package parameter. Hence provide full path like:
            # oamailer.actions.send
            modules[connector][ix] = {"module": import_module(api["import"])}
        return modules

    def run_api(self, api, payload, *args, connector, **kwargs):
        r = getattr(self.modules[connector][api]["module"], self.apis[connector][api]["action"])(
            **payload
        )
        return r

    def run_api_subprocess(self, api, payload, *args, connector, **kwargs):
        """
        runs api endpoint as a subprocess

        """
        logPath = os.path.join(sts.logDir, f"{connector}.log")
        params = ["pipenv", "run", "python", "-m", "oamailer", "send"]
        for k, vs in payload.items():
            params.extend([f"--{k}", vs])
        with open(logPath, "a+") as f:
            f.write(f"\n{dt.now()}:\n")
            f.write(f"cwd: {self.apiEndpointDir}\n")
            # f.write(f"missing: {m}")
            try:
                response = "subprocess out: \n"
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
        return {"oamailer": "done"}
