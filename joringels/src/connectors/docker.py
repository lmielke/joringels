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
        shutil.copyfile(sourcePath, targetPath)

    def mk_src_target(self, exportPath:str, *args, targetDir: str, **kwargs):
        """ 
            exportPath: path/to/safeName.yml
            targetDir: dir/to/export/...
            NOTE: targetDir is not in arguments ! currently only works from program
            like: upload.main(**params, targetDir=sts.exportDir)
        """
        sourcePath = exportPath.replace(os.sep, "/")
        targetPath = os.path.join(targetDir, os.path.basename(sourcePath))
        return sourcePath, targetPath


def main(*args, **kwargs):
    return LOC(*args, **kwargs)
