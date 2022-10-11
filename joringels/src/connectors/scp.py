# ps_upload.py

import os, sys, getpass
import subprocess
import joringels.src.settings as sts
import joringels.src.get_soc as soc


class SCPPS:
    def __init__(self, *args, **kwargs):
        pass

    def upload(
        self,
        serverCreds: dict,
        localPath: str = None,
        rmPath: str = None,
        *args,
        safeName: str,
        **kwargs,
    ):
        localPath = localPath if localPath is not None else sts.prep_path(safeName)
        rmPath = rmPath if rmPath is not None else serverCreds["rmPath"]
        if os.name == "nt":
            bash = "powershell.exe"
            script = os.path.join(sts.settingsPath, "connectors", "scp.ps1")

        cmds = [
            bash,
            script,
            serverCreds["rmUserName"],
            serverCreds["rmHost"],
            localPath,
            rmPath.replace(f"C:\\Users\\{getpass.getuser()}", "~").replace(os.sep, "/"),
            serverCreds["rmKey"],
        ]
        p = subprocess.Popen(cmds, stdout=sys.stdout)
        p.communicate()


def main(*args, **kwargs):
    scp = SCPPS(*args, **kwargs)
    return scp
