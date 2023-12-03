# standard lib imports
import colorama as color

color.init()

import os, re, shutil, sys, time
import yaml
import unittest

# C:\Users\lars\python_venvs\libs\joringels\joringels\test\test_api_handler.py
# test package imports
import joringels.src.settings as sts
import joringels.src.helpers as helpers
import os

# print(f"\n__file__: {__file__}")


class Test_UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.safeName, cls.productName, cls.clusterName = "safe_one", None, None
        cls.kwargs = {
            "safeName": cls.safeName,
            "entryName": "safe_one",
            "productName": cls.productName,
            "clusterName": cls.clusterName,
            "key": "testing",
            "retain": True,
        }

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def prep_enc_path(cls, *args, **kwargs):
        pass

    def test_mk_encrypt_path(self, *args, **kwargs):
        encryptPath, decryptPath = helpers.mk_encrypt_path(self.safeName, *args, **kwargs)
        self.assertTrue(encryptPath.endswith(sts.eext))
        self.assertTrue(decryptPath.endswith(sts.fext))


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
