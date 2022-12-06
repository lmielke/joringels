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

    def mk_src_target(self, exportPath:str, targetPath: str, rmPath: str = None, *args, **kwargs):
        sourcePath = exportPath.replace(os.sep, "/")
        targetPath = os.path.join(targetPath, os.path.basename(sourcePath))
        return sourcePath, exportPath


def main(*args, **kwargs):
    return LOC(*args, **kwargs)
