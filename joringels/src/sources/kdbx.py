# kdbx.py
from datetime import datetime as dt
from pykeepass import PyKeePass as keePass
import os, re, yaml
from itertools import chain
from joringels.src.get_creds import Creds
import joringels.src.get_soc as soc

import colorama as color

color.init()

import joringels.src.settings as sts
import joringels.src.helpers as helpers


# jo load -n digiserver -pd wobbles -cn testing -src $secrets/aktuell_2021.kdbx
class KeePassSecrets:
    def __init__(self, *args, safeName, productName, clusterName, **kwargs):
        self.ip_address = soc.get_external_ip()
        self.safeName = safeName.lower()
        self.productName = productName
        self.clusterName = clusterName
        self.secrets, self._secrets = dict(), dict()  # _secrets contains raw data from kdbx
        self.secretsPath = self.get_source(*args, **kwargs)
        self.session = keePass(self.secretsPath, self.get_creds(*args, **kwargs))

    def get_creds(self, *args, key=None, **kwargs):
        creds = Creds(uName="KeePass", kName="Login key").set(key=key) if key is None else key
        return creds

    def read_safe_data(self, *args, **kwargs):
        self.dataSafe = self.parse_entry(self.safeName, sts.dataSafeGroup, *args, **kwargs)
        self.entryPaths = list(chain(*self.secrets[self.safeName]["safe_params"].values()))

    def read_cluster_data(self, *args, **kwargs):
        self.cluster = self.parse_entry(self.clusterName, self.productName, *args, **kwargs)

    def parse_entry(self, entryName, groupName, *args, **kwargs):
        entry = self.get_entry(entryName=entryName, groupName=groupName)
        self.secrets.update(dict([self._parse_entry_params(entry)]))
        self.secrets[entryName].update(self._parse_attachments(entry))
        return entry

    def read_source(self, *args, entryName=None, **kwargs):
        self.read_safe_data(*args, **kwargs)
        self.read_cluster_data(*args, **kwargs)
        for entryPath in self.entryPaths:
            groupName, entryName = entryPath.split("/")[-2:]
            self.parse_entry(entryName, groupName, *args, **kwargs)
        return self.secrets

    def get_entry(self, *args, entryName, groupName, **kwargs):
        entry = self.session.find_entries(
            title=entryName, group=self.session.find_groups(name=groupName, first=True), first=True
        )
        if entry is None and entryName == self.safeName:
            msg = f"KDBX.ERROR get_entry: dataSafe not found: {entryName} in {groupName}"
            print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
            exit()
        elif entry is None:
            msg = f"KDBX.WARNING: No entry named: {entryName} in {groupName}"
            print(f"{color.Fore.YELLOW}{msg}{color.Style.RESET_ALL}")
        return entry

    def get_source(self, *args, source=None, **kwargs):
        """
        for kdbx source is the path to the kdbx file
        """
        if source is None or source == "kdbx":
            secretsPath = helpers.unalias_path(os.environ.get("secrets"))
        elif os.path.isfile(source):
            secretsPath = helpers.unalias_path(source)
        else:
            msg = f"KDBX.ERROR get_source: source not found: {source}"
            print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
            exit()
        return secretsPath

    def _parse_entry_params(self, entry: object, *args, **kwargs):
        entryParams = {
            "title": entry.title,
            "username": entry.username,
            "password": entry.password,
            "url": entry.url,
        }
        return entry.title, entryParams

    def _parse_attachments(self, entry: object, *args, **kwargs):
        attachments = {}
        for a in entry.attachments:
            try:
                attachments[os.path.splitext(a.filename)[0]] = yaml.safe_load(a.data)
            except Exception as e:
                print(f"KDBX.ERROR: keepass._parse_attachments: {e}")
        return attachments

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        pass


def main(action=None, *args, **kwargs):
    inst = KeePassSecrets(action, *args, **kwargs)
    if action is None:
        return inst
    else:
        return getattr(inst, action)(*args, **kwargs)
