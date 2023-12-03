# get_secrets.py

from datetime import datetime as dt
from pykeepass import PyKeePass as keePass
import os, re, yaml
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
        self.session = None

    def mk_session(self, *args, **kwargs):
        self.session = keePass(self.secretsPath, self.get_creds(*args, **kwargs))
        self.dataSafe = self.get_entry(entryName=self.safeName, groupName=sts.dataSafeGroup)
        self.cluster = self.get_entry(entryName=self.clusterName, groupName=self.productName)

    def get_creds(self, *args, key=None, **kwargs):
        creds = key if key is not None else Creds(uName="KeePass", kName="Login key").set(key=key)
        return creds

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

    def parse_entries(self, *args, **kwargs):
        """
        entries are the dataSafe the cluster and from the cluster_params
        the targets and entries
        this parses all those entries and populate self._secrets (metha dictionary)
        for latter generation of self.secrets
        """
        self.parse_entry(self.dataSafe, *args, **kwargs)
        self.parse_entry(self.cluster, *args, **kwargs)
        dataSafeParams = self._secrets[self.safeName]["attachments"]["safe_params"]
        # parse remaining entries and add to _secrets
        for entryPath in dataSafeParams["targets"] + dataSafeParams["entries"]:
            groupName, entryName = entryPath.split("/")[-2:]
            entry = self.get_entry(entryName=entryName, groupName=groupName)
            self.parse_entry(entry, *args, **kwargs)

    def parse_entry(self, *args, **kwargs) -> str:
        title, entryParams = self._parse_entry_params(*args, **kwargs)
        attachments = self._parse_attachments(*args, **kwargs)
        self._secrets[title] = {"entryParams": entryParams, "attachments": attachments}
        return title

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

    def read_source(self, *args, **kwargs):
        if self.session is None:
            self.mk_session(*args, **kwargs)
        # using self.session kdbx reads from the kdbx database
        self.parse_entries(*args, **kwargs)
        self.mk_secrets(*args, **kwargs)
        return self.secrets

    def mk_secrets(self, *args, **kwargs):
        for k, vs in self._secrets.items():
            if k == self.safeName:
                self.secrets[self.safeName] = {}
                for k1, vs1 in vs.items():
                    if k1 != "attachments" or vs1 != {}:
                        self.secrets[self.safeName].update(vs1)
                    else:
                        self.secrets[self.safeName][k1] = vs1
            elif k == self.clusterName:
                self.secrets[self.clusterName] = {}
                for k1, vs1 in vs.items():
                    if k1 == "entryParams":
                        self.secrets[self.clusterName].update(vs1)
                    elif k1 == "attachments":
                        clusterParams = vs1.get("cluster_params")
                        clusterParams[sts.appParamsFileName]["allowedClients"].append(
                            self.ip_address
                        )
                        self.secrets[self.clusterName].update(clusterParams)
            else:
                self.secrets[k] = {}
                for k1, vs1 in vs.items():
                    if k1 != "attachments" or vs1 != {}:
                        self.secrets[k].update(vs1)

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
