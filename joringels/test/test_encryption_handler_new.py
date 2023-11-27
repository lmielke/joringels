# standard lib imports
import colorama as color

color.init()

import os, re, shutil, sys, time
import yaml
import unittest

# test package imports
import joringels.src.settings as sts
import joringels.src.helpers as helpers
from joringels.src.encryption_handler_new import Handler as Handler


# print(f"\n__file__: {__file__}")


class Test_UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.prep_enc_path(*args, **kwargs)
        cls.tempDataPath = os.path.join(sts.testDataDir, "temp")
        cls.testKey = "testKey"
        time.sleep(1)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        try:
            shutil.rmtree(cls.tempDataPath, ignore_errors=False, onerror=None)
            # pass
        except Exception as e:
            print(f"UnitTest, tearDownClass, e: {e}")
        if os.path.exists(cls.encryptPath):
            os.remove(cls.encryptPath)

    @classmethod
    def prep_enc_path(cls, *args, **kwargs):
        cls.encryptPath = os.path.join(sts.testDataDir, "safe_one.yml")
        if os.path.exists(cls.encryptPath):
            return True
        cls.encryptBackup = os.path.join(sts.testDataDir, "#safe_one.yml")
        # copying this file is needed because pre-commit fails on changes
        shutil.copyfile(cls.encryptBackup, cls.encryptPath)

    def mk_test_data(cls, fileDir, fileName="test_secrets", *args, **kwargs):
        """
        test files to be encrypted are created on the fly inside a temp directory
        """
        if not os.path.isdir(fileDir):
            os.makedirs(fileDir)
        testFileName = f"{sts.decPrefix}{fileName}.yml"
        testData = {"Joringel": "Jorinde"}
        with open(os.path.join(fileDir, testFileName), "w") as f:
            f.write(yaml.dump(testData))
        return os.path.join(fileDir, testFileName)

    def test_mk_paths(self, *args, **kwargs):
        ### finds parameter fieles by serching throu relevant joringels/app folders and packages
        testPath = self.mk_test_data(self.tempDataPath, "mk_paths", *args, **kwargs)
        inst = Handler(testPath, *args, key=self.testKey)
        self.assertEqual(
            (
                os.path.join(self.tempDataPath, "mk_paths.yml"),
                os.path.join(self.tempDataPath, "decrypted_mk_paths.yml"),
            ),
            inst.mk_paths(testPath),
        )

    def test_file_encrypt(self, *args, **kwargs):
        """
        mk_test_data creates a file_encrypt.yml file which is then encrypted
        """
        testPath = self.mk_test_data(self.tempDataPath, "file_encrypt", *args, **kwargs)
        inst = Handler(testPath, *args, key=self.testKey)
        inst.file_encrypt(*args, **kwargs)
        assert os.path.isfile(inst.encryptPath)
        # not working
        # with open(inst.encryptPath, 'r') as enc:
        #     self.assertRaises(UnicodeDecodeError, enc.read())

    def test_file_decrypt(self, *args, **kwargs):
        testPath = self.mk_test_data(self.tempDataPath, "file_decrypt", *args, **kwargs)
        inst = Handler(testPath, self.testKey, *args, key=self.testKey)
        inst.file_encrypt(*args, **kwargs)
        inst.file_decrypt(*args, **kwargs)
        with open(inst.decryptPath, "r") as dec:
            self.assertEqual(dec.read().strip(), "Joringel: Jorinde")


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
