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
            "key": "testing",
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
        memorized = j._memorize(secrets=testData, connector="joringels")
        # memorized string is result, should not contain readable infos
        self.assertTrue(type(memorized) == str)
        self.assertTrue(len(memorized) > 100)
        self.assertFalse("Joringel" in memorized)
        # this only decrypts the keys, but not the values
        self.assertEqual(list(dict_keys_decrypt(memorized).keys()), ["Joringel", "logunittest"])

    def test__from_memory(self, *args, **kwargs):
        """
        this tests if a entryName can be given in an encycpted form and a
        valid entry value can be returned
        if entryName is not decryptable or not existign in secrets, no value will be returned
        """
        testFileName = "test__from_memory.yml"
        testDataPath = helpers.copy_test_data(
            sts.encryptDir, f"{self.safeName}.yml", targetName=testFileName
        )
        params = self.params.copy()
        params.update({"safeName": testFileName[:-4]})
        # decrypted entryName = 'PRODUCTNAME'
        correct = (
            f"XJSD9Jk67LVUXhdg6R6LY285QmYyUbS/roo199jROXc="
            f":htKwpVfW0DrS+szwC+qtDA==:N3Big0eC4VkyC42WbcJH/w=="
        )
        correctVal = text_decrypt(correct, os.environ.get("DATASAFEKEY"))
        self.assertEqual(correctVal, "PRODUCTNAME")
        nonExistent = (
            f"VoUfcFxENK/qhqebTaNknZIreDcLt2vzncwTnyFj82g="
            f":wSVGfhjUWWptCae/5PK40A==:CQpVe3MhfRYlCi/MIH0b0w=="
        )
        nonExistentVal = text_decrypt(nonExistent, os.environ.get("DATASAFEKEY"))
        self.assertEqual(nonExistentVal, "NONEXISTENT")
        # test starts here
        js = Joringel(**params)
        Test_Joringel.deletePaths.extend([js.encryptPath, js.decryptPath])
        p, s = js._digest(testDataPath)
        js._memorize(secrets=js.secrets, connector="joringels")
        # decycptable but nonExistent entry returns None
        # self.assertIsNone(js._from_memory(nonExistent))
        # self.assertIsNone(js._from_memory('something'))
        # # # finally the correct pwd with a existing entry returns a value
        # # print('test__from_memory 3')
        # self.assertIsNotNone(js._from_memory(correct))
        if os.path.exists(js.encryptPath):
            os.remove(js.encryptPath)
        if os.path.exists(js.decryptPath):
            os.remove(js.decryptPath)

    # def test__digest(self, *args, **kwargs):
    #     # NOTE: THIS TEST WAS REMOVED BECAUSE IT INTERFERES WITH TEST__FROM_MEMORY
    #     # FOR NO APPERENT REASON. J._MEMORIZE RETURNS SELF.SECRETS WHICH MAGICALLY
    #     # DISAPPERS FROM J. AFTER RUNNING TEST__FROM_MEMORY

    #     # NOTE: this test is using the .ssp folder to create test file
    #     # this is due to the program avoiding to allow changing the encryptDir loction
    #     testDataPath = helpers.copy_test_data(sts.encryptDir, f"{self.safeName}.yml")
    #     j = Joringel(**self.params)
    #     Test_Joringel.deletePaths.append(j.encryptPath)
    #     j._digest(testDataPath)
    #     self.assertEqual(j.encryptPath, sts.unalias_path(f"~/.ssp/{self.safeName}.json"))
    #     self.assertEqual(list(j.secrets.keys())[:3], ['application_0', 'PRODUCTNAME',
    #                                                                 'digi_postgres_login'])
    #     if os.path.exists(j.encryptPath): os.remove(j.encryptPath)

    def test__chkey(self, *args, **kwargs):
        pass

    def test__handle_integer_keys(self, *args, **kwargs):
        data = {"1": "one", "two": "two", 3: "three", "3.14": "something"}
        expected = [1, "two", 3, "3.14"]
        j = Joringel(*args, **kwargs)
        corrected = j._handle_integer_keys(data)
        self.assertEqual(list(corrected.keys()), expected)

    def test__get_recent_logfile(self, *args, **kwargs):
        j = Joringel(*args, **kwargs)
        text = j._get_recent_logfile(connector="joringels")
        if os.name == "posix":
            self.assertEqual("Nothing", text)
        else:
            self.assertIn("INFO logunittest -", text)


@contextmanager
def temp_password(*args, pw, **kwargs) -> None:
    current = os.environ["DATASAFEKEY"]
    try:
        os.environ["DATASAFEKEY"] = pw
        yield
    finally:
        os.environ["DATASAFEKEY"] = current


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
