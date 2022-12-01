# ps_upload.py

import os, sys, getpass
import subprocess
import joringels.src.settings as sts
import joringels.src.helpers as helpers
import joringels.src.get_soc as soc


class SCPPS:
    def __init__(self, *args, **kwargs):
        pass

    def upload(
        self,
        localPath: str,
        rmPath: str = None,
        *args,
        url: str,
        username: str,
        password: str = None,
        **kwargs,
    ):
        localPath = localPath.replace(os.sep, "/")
        rmPath = os.path.dirname(localPath.replace(f"C:/Users/{getpass.getuser()}", "~"))
        cmds = [
            "powershell.exe",
            os.path.join(sts.settingsPath, "connectors", "scp.ps1"),
            url,
            localPath,
            rmPath,
            username,
            password,
        ]
        p = subprocess.Popen(cmds, stdout=sys.stdout)
        p.communicate()


def main(*args, **kwargs):
    scp = SCPPS(*args, **kwargs)
    return scp
