# get_creds.py
import os, sys
from getpass import getpass as gp

# colors for printing
import colorama as color

color.init()
COL_RM = color.Style.RESET_ALL
YELLOW = color.Fore.YELLOW
GREEN = color.Fore.GREEN
RED = color.Fore.RED


class Creds:
    def __init__(self, *args, uName=None, kName="key", **kwargs):
        self.rules = None  # implement key rules here
        self.kName = kName
        self.uName = uName

    def set(self, *args, force=True, confirmed=True, key=None, **kwargs):
        msg = f"{self.uName} {YELLOW}{self.kName}{COL_RM}: "
        key = self.get_os_key(key, *args, **kwargs)
        if not key:
            while not key:
                key = gp(prompt=f"{msg.strip(': ')}: ", stream=None)
                if force == False:
                    break
            while not confirmed:
                confirmed = self._confirm_equals(key, *args, **kwargs)
        key = self.get_os_key(key, *args, **kwargs)
        return key

    def get_os_key(self, key, *args, safeName=None, **kwargs):
        if key == "os":
            kName = "DATAKEY" if self.kName.endswith("eyV") else "DATASAFEKEY"
            key = os.environ[kName]
            msg = f"\t {self.uName}, {self.kName} Using $env:{kName}"
            print(f"{color.Fore.YELLOW}{msg}{color.Style.RESET_ALL}")
        return key

    def _confirm_equals(self, key, *args, **kwargs):
        # getting new key
        confirmKey = None
        while confirmKey != key:
            confirmKey = gp(prompt=f"\tre-type key to continue: ", stream=None)
        return True

    def resolve_key(self, key, *args, **kwargs):
        if key is None or key == "os":
            key = os.environ["DATASAFEKEY"] if self.kName == "key" else os.environ["DATAKEY"]
        elif key == "init":
            key = os.environ["INSTALLPASS"]
        return key
