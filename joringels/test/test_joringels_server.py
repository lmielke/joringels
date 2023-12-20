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
from joringels.src.joringels_server import JoringelsServer
from joringels.src.encryption_dict_handler import text_encrypt, dict_encrypt, dict_decrypt
from logunittest.settings import get_testlogsdir as logunittest_logs_dir

# print(f"\n__file__: {__file__}")


class Test_JoringelsServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        cls.tempDirName = "temp_test_joringels_server"
        cls.tempDataDir = helpers.mk_test_dir(cls.tempDirName)
        cls.logDir = os.path.join(logunittest_logs_dir(), "joringels")
        cls.safeName = "test_joringels_safe"
        cls.params = params = {
            "safeName": cls.safeName,
            "productName": "haimdall",
            "clusterName": "testing_cluster",
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

    @helpers.test_setup("safe_one.json", os.getcwd())  # see helpers.test_setup docstring
    def test__prep_api_params(self, tempDataPath, *args, **kwargs):
        params = self.params.copy()
        params.update({"safeName": "safe_one", "connector": "haimdall"})
        js = JoringelsServer(**params)
        js.encryptPath = tempDataPath
        js._digest(*args, **params)
        js._prep_api_params(*args, **params)
        self.assertEqual(js.apiParams.connector, params.get("connector"))
        self.assertIsNotNone(js.apiParams.api[0])
        self.assertEqual(
            js.apiParams.api[0],
            {"import": "haimdall.actions.communicate", "action": "send", "response": None},
        )

    @helpers.test_setup("safe_one.json", os.getcwd())  # see helpers.test_setup docstring
    def test__from_memory(self, tempDataPath, *args, **kwargs):
        params = self.params.copy()
        params.update({"safeName": "safe_one", "connector": "joringels"})
        # prep test create a JoringelsServer instance with encypted secrets
        js = JoringelsServer(**params)
        js.encryptPath = tempDataPath
        js.server(*args, **params)
        # passing valid entryName to _from_memory should retrieve
        # the encrypted secrets for that entryName
        outEnc = js._from_memory(text_encrypt(params["clusterName"], params["key"]))
        outDec = dict_decrypt(outEnc)
        self.assertEqual(list(outDec)[0], params["clusterName"])
        self.assertIsNotNone(outEnc)
        # passing a non existing entryName to _from_memory should return None
        outNone = js._from_memory(text_encrypt("NonExistingEntry", params["key"]))
        self.assertIsNone(outNone)


if __name__ == "__main__":
    unittest.main()
