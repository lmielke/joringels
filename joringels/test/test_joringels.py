# standard lib imports
import colorama as color

color.init()
from contextlib import contextmanager
import os, re, shutil, sys, time
import yaml
import unittest

# C:\Users\lars\python_venvs\libs\joringels\joringels\test\test_api_handler.py
# test package imports
import joringels.src.settings as sts
import joringels.src.helpers as helpers
from joringels.src.joringels import Joringel
from joringels.src.encryption_dict_handler import (
    text_decrypt,
    text_encrypt,
    dict_keys_encrypt,
    dict_keys_decrypt,
    dict_values_decrypt,
    dict_values_encrypt,
)

from logunittest.settings import get_testlogsdir as logunittest_logs_dir

# print(f"\n__file__: {__file__}")


class Test_Joringel(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        cls.tempDirName = "temp_test_joringels"
        cls.tempDataDir = helpers.mk_test_dir(cls.tempDirName)
        cls.logDir = os.path.join(logunittest_logs_dir(), "joringels")
        cls.safeName = "test_joringels_safe"
        cls.params = params = {
            "safeName": cls.safeName,
            "productName": "haimdall",
            "clusterName": "testing",
            "key": sts.testKeyOuter,
            "keyV": sts.testKeyInner,
            # never remove retain, it will break the test
            "retain": True,
        }
        cls.deletePaths = []

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        helpers.rm_test_dir(cls.tempDataDir)
        try:
            for path in cls.deletePaths:
                if os.path.exists(path):
                    os.remove(path)
        except:
            pass

    def test__memorize(self, *args, **kwargs):
        testData = helpers.load_yml(helpers.mk_test_file(self.tempDataDir, "test__memorize.yml"))
        j = Joringel(*args, **kwargs)
        j.secrets = testData
        j._memorize(connector="joringels")
        # j.secrets string is result, should not contain readable infos
        self.assertTrue(type(j.secrets) == str)
        self.assertTrue(len(j.secrets) > 100)
        self.assertFalse("Joringel" in j.secrets)
        # this only decrypts the keys, but not the values
        self.assertEqual(list(dict_keys_decrypt(j.secrets).keys()), ["Joringel"])

    def test__chkey(self, *args, **kwargs):
        pass

    def test__handle_integer_keys(self, *args, **kwargs):
        data = {"1": "one", "two": "two", 3: "three", "3.14": "something"}
        expected = [1, "two", 3, "3.14"]
        j = Joringel(*args, **kwargs)
        corrected = j._handle_integer_keys(data)
        self.assertEqual(list(corrected.keys()), expected)


if __name__ == "__main__":
    with helpers.temp_password(pw=sts.testKeyOuter):
        unittest.main()
