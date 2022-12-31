# standard lib imports
import colorama as color

color.init()

import os, re, shutil, sys, time
import yaml
import unittest

# C:\Users\lars\python_venvs\libs\joringels\joringels\test\test_upload.py
# test package imports
import joringels.src.settings as sts
import joringels.src.helpers as helpers
from joringels.src.actions import upload

# print(f"\n__file__: {__file__}")


class UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.prep_enc_path(*args, **kwargs)
        cls.testData = cls.get_test_data(*args, **kwargs)
        # self.upload = upload.main(*args, **cls.testData['kwargs'])

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        if os.path.exists(cls.encryptPath):
            os.remove(cls.encryptPath)

    @classmethod
    def get_test_data(cls, *args, **kwargs):
        with open(os.path.join(sts.testDataDir, "test_upload.yml"), "r") as f:
            return yaml.safe_load(f)

    @classmethod
    def prep_enc_path(cls, *args, **kwargs):
        cls.encryptPath = os.path.join(sts.testDataDir, "safe_one.yml")
        if os.path.exists(cls.encryptPath):
            return True
        cls.encryptBackup = os.path.join(sts.testDataDir, "#safe_one.yml")
        # copying this file is needed because pre-commit fails on changes
        shutil.copyfile(cls.encryptBackup, cls.encryptPath)

    def test_get_targets(self, *args, **kwargs):
        expected_names = ["joringels_server", "haimdall_server"]
        expected_targets = (
            "python_venvs/physical_machines/haimdall_server",
            "python_venvs/physical_machines/joringels_server",
        )


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
