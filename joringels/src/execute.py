# toserver.py
import os
from joringels.src.kdbx import KeePassSecrets
from joringels.src.scp import SCPPS
from joringels.src.joringels import Joringel
from joringels.src.jorinde import Jorinde
import joringels.src.settings as sts
import joringels.src.helpers as helpers


class Processes:
    def __init__(self, action, *args, source, method, **kwargs):
        self.action = action
        self.sources = {
            "kdbx": KeePassSecrets,
        }
        self.source = self.sources.get(source)
        self.methods = {
            "ps": SCPPS,
        }
        self.method = self.methods.get(method)

    def upload(self, *args, key, **kwargs) -> None:
        filePath = self._mk_paths(*args, **kwargs)
        s = self.source(*args, **kwargs)
        filePath, serverCreds = s.load(filePath, *args, **kwargs)
        # kdbx key is replaced by secreatskey
        kwargs.update({"key": s.secrets["key"]})
        filePath, _ = self.digest(*args, **kwargs)
        self.method(*args, **kwargs).upload(filePath, serverCreds, *args, **kwargs)

    def _mk_paths(self, *args, safeName, **kwargs) -> str:
        fileName = f"{sts.decPrefix}{safeName}.yml"
        filePath = helpers.prep_path(os.path.join(sts.encryptDir, fileName))
        return filePath

    def fetch(self, *args, **kwargs):
        Jorinde(*args, verbose=verbose, **kwargs).fetch(*args, **kwargs)

    def load(self, *args, **kwargs):
        KeePassSecrets(*args, **kwargs).load(*args, **kwargs)

    def serve(self, action, *args, **kwargs):
        Joringel(action, *args, **kwargs).serve(*args, **kwargs)

    def digest(self, action, *args, **kwargs):
        j = Joringel(action, *args, **kwargs)
        return j._digest(*args, **kwargs)

    def chkey(self, action, *args, **kwargs):
        Joringel(action, *args, **kwargs).chkey(*args, **kwargs)
