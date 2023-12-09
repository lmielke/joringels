# api_handler.py
import joringels.src.settings as sts
import joringels.src.helpers as helpers
from importlib import import_module
import os, sys
from datetime import datetime as dt
import subprocess
from logunittest.settings import get_testlogsdir


class ApiHandler:
    def __init__(self, *args, connector, verbose=0, **kwargs):
        self.connector = connector
        self.apiEndpointDir = helpers.get_api_enpoint_dir(connector)
        # self.safeName = safeName
        self.verbose = verbose

    def _import_api_modules(self, *args, apis, **kwargs) -> None:
        """fills self.modules with imported modules from api import string
        self.modules is used to keep imported modules and avoid import on demand
        result looks like: {
                0: {'module': <module 'oamailer.actions.send' from ...},
                1: ...
                }
        """
        sys.path.append(self.apiEndpointDir)
        self.modules, self.apis = {}, apis
        for ix, api in self.apis.items():
            # import_module without package parameter. Hence provide full path like:
            # oamailer.actions.send
            module = import_module(api["import"])
            self.modules[ix] = {"module": module}
            if ix == 0:
                package = module.__package__.split(".")[-1]
        self.modules["logunittest"] = self._get_recent_logfile(*args, **kwargs)

    def run_api(self, api: int, payload: dict, *args, connector: str, **kwargs):
        """
        gets a pre imported module from self.modules by its name (connector)
        selects the execuable function/action by its index (api)
        calls the target package function passing in payload like **kwargs
        """
        r = getattr(self.modules[api]["module"], self.apis[api]["action"])(**payload)
        return r

    def _get_recent_logfile(self, *args, **kwargs):
        """
        This is part of the serve/up strategy and allowes to remotely check
        if upping was successfull and joringels runs without errors by checking
        unittest result logs.
        relies on logunittest to be installed and run before 'jo serve'
        jo fetch -e logunittest -ip hostip
        """
        from logunittest.logunittest import Coverage
        from logunittest.actions import stats

        # get header from latest test logfile
        testLogDir = get_testlogsdir()
        cov = Coverage(logDir=testLogDir)
        cov.get_stats()
        logResults = f" | {cov.latest[0]} | [{stats.main().split('[')[-1]}"
        return logResults

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
