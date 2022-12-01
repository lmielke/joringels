# ps_upload.py

import os, shutil, sys
import joringels.src.settings as sts
import joringels.src.helpers as helpers


class LOC:
    def __init__(self, *args, **kwargs):
        print(f"__init__kwargs: \n{kwargs}")
        self.singleSource = True

    def upload(self, *args, **kwargs):
        sourcePath, targetPath = self.mk_src_target(*args, **kwargs)
        print(f"\n\tcopying from: {sourcePath} to {targetPath}")
        shutil.copyfile(sourcePath, targetPath)

    def mk_src_target(self, exportDir:str, localPath: str, rmPath: str = None, *args, **kwargs):
        sourcePath = localPath.replace(os.sep, "/")
        targetPath = os.path.join(exportDir, os.path.basename(sourcePath))
        return sourcePath, targetPath


def main(*args, **kwargs):
    return LOC(*args, **kwargs)
