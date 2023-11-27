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
from joringels.src.api_handler import ApiHandler

# print(f"\n__file__: {__file__}")


class Test_UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.prep_enc_path(*args, **kwargs)
        cls.testData = cls.get_test_data(*args, **kwargs)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        if os.path.exists(cls.encryptPath):
            os.remove(cls.encryptPath)

    @classmethod
    def get_test_data(cls, *args, **kwargs):
        with open(os.path.join(sts.testDataDir, "test_api_handler.yml"), "r") as f:
            return yaml.safe_load(f)

    @classmethod
    def prep_enc_path(cls, *args, **kwargs):
        cls.encryptPath = os.path.join(sts.testDataDir, "safe_one.yml")
        if os.path.exists(cls.encryptPath):
            return True
        cls.encryptBackup = os.path.join(sts.testDataDir, "#safe_one.yml")
        # copying this file is needed because pre-commit fails on changes
        shutil.copyfile(cls.encryptBackup, cls.encryptPath)

    def test__initialize_apis(self, *args, name="_initialize_apis", **kwargs):
        instance = ApiHandler(*args, **kwargs)
        expected = {
            "oamailer": {
                0: {"import": "oamailer.actions.send", "action": "send", "response": None}
            }
        }
        data = self.testData[sts.apiParamsFileName]
        data["oamailer"] = {str(k): vs for k, vs in data["oamailer"].items()}
        out = instance._initialize_apis(*args, apis=data, connector="oamailer", **kwargs)
        self.assertEqual(expected, out)

    def test__import_api_modules(self, *args, name="_import_api_modules", **kwargs):
        """This test will throw an exception as shown in expected, because
        it has to be called from the oamailer executable. However, since this unittest
        uses joringels executable I only test, that joringels
        attempts to import the correct module. (oamailer with google_auth_authlib)
        """
        instance = ApiHandler(*args, **kwargs)
        # path to import module
        instance.apiEndpointDir = r"C:/Users/lars/python_venvs/modules/oamailer"
        # api to import the module for with import statement and action
        instance.apis = {
            "oamailer": {
                0: {"import": "oamailer.actions.send", "action": "send", "response": None}
            }
        }
        # oamailer import will fail in this test, but in reality it should NOT fail.
        expected = "ModuleNotFoundError: No module named 'google_auth_oauthlib'"
        with self.assertRaises(Exception) as context:
            instance._import_api_modules(
                *args, secrets=self.testData, safeName="oamailer", **kwargs
            )
            self.assertTrue(expected in str(context.exception))


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
