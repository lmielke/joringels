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
    def __init__(self, action, *args, safeName, source=None, verbose=0, key=None, **kwargs):
        self.verbose = verbose
        self.groups, self.safeName = {}, safeName.lower()
        self.secrets, self.secretsKey, self.serverCreds = {}, "", {}
        # self.kPath = self._check_kPath(*args, **kwargs)
        self.creds = (
            key
            if key is not None
            else Creds(*args, **kwargs).set("KeePass login", *args, **kwargs)
        )
        source = source if source is not None else helpers.unalias_path(os.environ.get("secrets"))
        self.session = keePass(source, self.creds)
        self.dataSafes = self.session.find_groups(name=sts.dataSafeGroup, first=True)
        self.dataSafe = self.session.find_entries(title=safeName, group=self.dataSafes, first=True)
        if not self.dataSafe:
            msg = f"KDBX.ERROR: No dataSafe found with name: {safeName} in {self.dataSafes}"
            print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
            exit()
        self.dataSafePath = "/".join(self.dataSafe.path)
        self.cluster = self.get_cluster(*args, **kwargs)
        if action != "show":
            self.targets, self.entries = self._get_safe_params(*args, **kwargs)

    def get_cluster(self, *args, clusterName: str = None, productName: str = None, **kwargs):
        self.clusterName = clusterName
        if self.clusterName is not None:
            if not productName:
                msg = f"KDBX.ERROR: No productName: {productName}"
                print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
                exit()
            clusters = self.session.find_groups(name=productName)[0]
            cluster = self.session.find_entries(title=clusterName, group=clusters, first=True)
            if cluster is None:
                msg = f"KDBX.ERROR: No cluster named: {clusterName} in {productName}"
                print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
                exit()
            return cluster
        else:
            return None

    def _get_safe_params(self, *args, **kwargs) -> list:
        """
        reads entries and gets attachments from the datasafe

        """
        if self.dataSafe is None:
            msg = (
                f"{color.Fore.RED}"
                f"KDBX.ERROR: s._get_safe_params with safeName not found: {self.safeName}"
                f"{color.Style.RESET_ALL}"
            )
            print(msg)
            exit()
        self.encrpytKey = self.dataSafe.password
        attachs = self._get_attachments(self.dataSafe)
        if not attachs:
            msg = (
                f"{color.Fore.RED}"
                f"KDBX.ERROR: s._get_safe_params no attachment named {sts.safeParamsFileName}"
                f" for {self.safeName}"
                f"{color.Style.RESET_ALL}"
            )
            print(msg)
            exit()

        safe_params = attachs.get(sts.safeParamsFileName)
        # self.joringelsParams = attachs.get(sts.appParamsFileName, {})
        targets = dict([reversed(os.path.split(p)) for p in safe_params["targets"]])
        entries = safe_params["entries"]
        entries.append(self.dataSafePath)
        if self.clusterName is not None:
            entries.append("/".join(self.cluster.path))
        return targets, entries

    def _get_entries_params(self, entries, *args, productName, clusterName, **kwargs):
        for i, entryPath in enumerate(entries):
            self.verbose: print(f"{entryPath = }")
            groupPath, entryName = os.path.split(entryPath)
            if self.verbose:
                print(f"\n_get_entries_params {i} {groupPath = }, {entryName = }")
            entries = self.session.find_entries(
                title=entryName, group=self.session.find_groups(path=groupPath)
            )
            # for enttry with productName/clusterName pykeepass finds multiple entries
            # but needs to be a single entry
            if len(entries) >= 2:
                for e in entries:
                    if productName in e.path and clusterName in e.path:
                        entry = e
                        break
                else:
                    entry = entries[0]
            else:
                entry = entries[0]
            self.secrets[entry.title] = self._get_entry_params(entry, *args, **kwargs)
            self.secrets[entry.title].update(self._get_attachments(entry, *args, **kwargs))

    def get_ip_address(self, *args, **kwargs):
        ip_address = soc.get_external_ip()
        if ip_address is not None:
            try:
                # add_ip_addres is a recursive loop that falls back to here
                self.add_ip_address(self.secrets[self.clusterName], ip_address)
            except:
                pass
        return ip_address

    def add_ip_address(self, objs, ip_address, *args, **kwargs):
        """
        recursive loop that raises back to calling function try except block
        finds the dict containing key sts.allowedClients by looping the input dict
        and adds external ip to all allowedClients lists
        """
        found = False
        for objName, obj in objs.items():
            if type(obj) is dict:
                if sts.allowedClients in obj:
                    found = True
                    obj[sts.allowedClients].append(ip_address)
                else:
                    self.add_ip_address(obj, ip_address)
        if found:
            raise
        return False

    def _get_entry_params(self, entry, *args, **kwargs):
        if entry is None:
            msg = f"KDBX.ERROR:_get_entries_params, entry not found: {entry}"
            print(f"{color.Fore.YELLOW}{msg}{color.Style.RESET_ALL}")
            exit()
        entryParams = {
            "title": entry.title,
            "username": entry.username,
            "password": entry.password,
            "url": entry.url,
        }
        return entryParams

    def _get_attachments(self, entry, *args, **kwargs):
        attachs = {}
        for a in entry.attachments:
            try:
                attachs[os.path.splitext(a.filename)[0]] = yaml.safe_load(a.data)
            except Exception as e:
                print(f"keepass._get_attachments: {e}")
        return attachs

    def _write_secs(self, *args, safeName, filePrefix=None, **kwargs):
        filePrefix = filePrefix if filePrefix else sts.decPrefix
        fileName = f"{filePrefix}{safeName}.yml"
        filePath = helpers.prep_path(os.path.join(sts.encryptDir, fileName))
        # file extension is .yml
        with open(filePath, "w") as f:
            f.write(yaml.dump(self.secrets))

    def load(self, *args, host=None, productName: str = None, **kwargs) -> None:
        if self.verbose >= 2:
            self.show(host, *args, **kwargs)
        host = host if host is not None else list(self.targets)[0]
        target = self.targets.get(host, None)
        self._get_entries_params(self.entries, productName=productName, *args, **kwargs)
        self._get_entries_params(self.targets, productName=productName, *args, **kwargs)
        if productName is not None:
            self.secrets["PRODUCTNAME"] = productName
        self.get_ip_address(*args, **kwargs)
        self._write_secs(*args, **kwargs)
        return self.dataSafePath

    def show(self, searchTerm=None, *args, **kwargs) -> None:
        """
        gets all relevant entry paths from keepass and prints them in a copy/paste
        optimized way

        run like:   python -m joringels.src.sources.kdbx show -n python_venvs
                    enter keepass key when prompted
        copy the entries into the NOTES of you keepass joringels_data_save entry

        NOTE: Each safe needs one server login credential entry for upload
            server login credential start like: !~/python_venvs/.../...
            normal entries look like:             python_venvs/.../...
        """
        self.verbose = 1
        if self.verbose:
            msg = f"Available Groups: {searchTerm}"
            print(f"\n{color.Fore.YELLOW}{msg}{color.Style.RESET_ALL}")
        for i, element in enumerate(self.session.find_entries(title=".*", regex=True)):
            if element.path[0] == sts.kdbxRootGroup:
                entryPath = sts.kps_sep.join(element.path)
                if searchTerm is not None and searchTerm in entryPath:
                    return element
                else:
                    if self.verbose:
                        print(f"{i} copy to Notes:\t{entryPath}")


def main(action=None, *args, **kwargs):
    inst = KeePassSecrets(action, *args, **kwargs)
    if action is None:
        return inst
    else:
        return getattr(inst, action)(*args, **kwargs)


if __name__ == "__main__":
    import joringels.src.arguments as arguments

    kwargs = arguments.mk_args().__dict__
    keepass = main(**kwargs)
