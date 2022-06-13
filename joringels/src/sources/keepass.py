# get_secrets.py

from datetime import datetime as dt
from pykeepass import PyKeePass as keePass
import os, re, yaml
import colorama as color

color.init()
from getpass import getpass as gp

import joringels.src.settings as sts

# :)L0veMi11i0n$
class KeePassSecrets:
    def __init__(self, *args, groupName, key=None, **kwargs):
        self.groups, self.groupName = {}, groupName
        self.secrets, self.secretsKey, self.serverCreds = {}, "", {}
        self.session = keePass(
            sts.appParams.get("kPath"),
            key if key is not None else gp(prompt="KeePass: ", stream=None),
        )
        self.dataSafes = self.session.find_groups(name=sts.kpsGrpName, first=True)
        self.dataSafe = self.session.find_entries(
            title=groupName, group=self.dataSafes, first=True
        )
        self.targets, self.entries = self._get_safe_params(*args, **kwargs)

    def _get_safe_params(self, *args, **kwargs) -> list:
        if self.dataSafe is None:
            msg = f"keepass._get_safe_params with data_safe not found: {self.groupName}"
            print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
            return None, None
        self.encrpytKey = self.dataSafe.password
        attachments = self._get_attachments(self.dataSafe)
        safe_params = attachments.get(sts.safeParamsFileName)
        self.joringelsParams = attachments.get(sts.appParamsFileName)
        targets = dict([reversed(os.path.split(p)) for p in safe_params["targets"]])
        entries = safe_params["entries"]
        return targets, entries

    def load(self, *args, host=None, **kwargs) -> None:
        host = host if host is not None else list(self.targets)[0]
        target = self.targets.get(host, None)
        self._mk_server_params(target, host, *args, **kwargs)
        self._mk_secrets(*args, **kwargs)
        self.secrets[sts.appParamsFileName] = self.joringelsParams
        self._write_secs(*args, **kwargs)
        return self.serverCreds

    def _mk_secrets(self, *args, **kwargs):
        for entryPath in self.entries:
            groupPath, entryName = os.path.split(entryPath)
            group = self.session.find_groups(path=groupPath)
            entry = self.session.find_entries(title=entryName, group=group, first=True)
            if entry is None:
                print(f"keepass._extract_entries, entry not found: {entry}")
            self.secrets[entry.title] = {
                "key": self.encrpytKey,
                "title": entry.title,
                "username": entry.username,
                "password": entry.password,
                "url": entry.url,
            }
            if entry.attachments:
                self.secrets[entry.title].update(self._get_attachments(entry, *args, **kwargs))

    def _mk_server_params(self, target, host, *args, **kwargs):
        group = self.session.find_groups(path=target)
        entry = self.session.find_entries(title=host, group=group, first=True)
        self.serverCreds["rmUserName"] = entry.username
        self.serverCreds["rmKey"] = entry.password
        self.serverCreds["rmHost"] = entry.url
        self.serverCreds["rmPath"] = sts.encryptDir

    def _get_attachments(self, entry, *args, **kwargs):
        attachs = {}
        for a in entry.attachments:
            try:
                attachs[a.filename] = yaml.safe_load(a.data)
            except Exception as e:
                print(f"keepass._get_attachments: {e}")
        return attachs

    def _write_secs(self, *args, groupName, filePrefix=None, **kwargs):
        filePrefix = filePrefix if filePrefix else sts.appParams.get("decPrefix")
        fileName = f"{filePrefix}{groupName}.yml"
        filePath = sts.prep_path(os.path.join(sts.encryptDir, fileName))

        # file extension is .yml
        with open(filePath, "w") as f:
            f.write(yaml.dump(self.secrets))

    def show(self, *args, groupName: str, **kwargs) -> None:
        """
        gets all relevant entry paths from keepass and prints them in a copy/paste
        optimized way

        run like:   python -m joringels.src.sources.keepass show -g python_venvs
                    enter keepass key when prompted
        copy the entries into the NOTES of you keepass joringels_data_save entry

        NOTE: Each safe needs one server login credential entry for upload
            server login credential start like: !/python_venvs/.../...
            normal entries look like:             python_venvs/.../...
        """
        for i, element in enumerate(self.session.find_entries(title=".*", regex=True)):
            if element.path[0] == groupName:
                entryPath = sts.kps_sep.join(element.path)
                print(f"{i} copy to Notes:\t{entryPath}")


def main(action=None, *args, **kwargs):
    inst = KeePassSecrets(*args, **kwargs)
    if action is None:
        return inst
    else:
        return getattr(inst, action)(*args, **kwargs)


if __name__ == "__main__":
    import joringels.src.arguments as arguments

    kwargs = arguments.mk_args().__dict__
    keepass = main(**kwargs)
