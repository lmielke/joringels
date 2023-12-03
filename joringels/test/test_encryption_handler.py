# standard lib imports
import colorama as color

color.init()

import os, re, shutil, sys, time
import json
import yaml
import unittest

# test package imports
import joringels.src.settings as sts
import joringels.src.helpers as helpers
from joringels.src.encryption_handler import Handler as Handler
from joringels.src.encryption_dict_handler import dict_decrypt


# print(f"\n__file__: {__file__}")


class Test_UnitTest(unittest.TestCase):

    # test setup and teardown section
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.tempDirName = "temp_test_encryption_handler"
        cls.tempDataDir = helpers.mk_test_dir(cls.tempDirName)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        helpers.rm_test_dir(cls.tempDataDir)

    # test section starts here
    def test__mk_secrets_paths(self, *args, **kwargs):
        testPath = helpers.mk_test_file(self.tempDataDir, "test__mk_secrets_paths.yml")
        inst = Handler(testPath, *args, key=sts.testKey)
        encryptPath, decryptPath = inst._mk_secrets_paths(testPath)
        self.assertTrue(encryptPath.endswith(sts.eext))
        self.assertTrue(decryptPath.endswith(sts.fext))

    def test__get_file_data(self, *args, **kwargs):
        testPath = helpers.mk_test_file(self.tempDataDir, "test__get_file_data.yml")
        inst = Handler(testPath, *args, key=sts.testKey)
        inst._get_file_data(None, *args, **kwargs)
        self.assertEqual(inst.data["decrypted"], sts.testDataDict)

    def test_cryptonize(self, *args, **kwargs):
        testPath = helpers.mk_test_file(
            self.tempDataDir, "test_cryptonize.json", testDataStr=sts.cryptonizeDataStr
        )
        # testPath = Test_UnitTest.prep_enc_path(testFileName, *args, **kwargs)
        inst = Handler(testPath)
        inst.cryptonize(*args, **kwargs)
        encrypted = inst.data["encrypted"]
        self.assertTrue(len(encrypted) >= len(str(sts.testDataDict)) and not " " in encrypted)

    def test_cleanup(self, *args, **kwargs):
        testPath = helpers.mk_test_file(self.tempDataDir, "test_cleanup.json")
        # testPath = Test_UnitTest.prep_enc_path(testFileName, *args, **kwargs)
        inst = Handler(testPath)
        inst.cryptonize(*args, key=sts.testKey, keyV=sts.testKey, **kwargs)
        self.assertTrue(os.path.isfile(inst.encryptPath))
        inst.write_decrypted(*args, **kwargs)
        time.sleep(0.1)
        self.assertTrue(os.path.isfile(inst.decryptPath))
        time.sleep(0.1)
        inst.cleanup(*args, **kwargs)
        self.assertTrue(not os.path.isfile(inst.decryptPath))
        time.sleep(0.1)


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
