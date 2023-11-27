# standard lib imports
import colorama as color

color.init()

import os, re, shutil, sys, time
import yaml
import unittest

# test package imports
import joringels.src.settings as sts
import joringels.src.helpers as helpers
import joringels.src.encryption_dict_handler as handler


# print(f"\n__file__: {__file__}")


class Test_UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.prep_enc_path(*args, **kwargs)
        cls.testDataDir = os.path.join(sts.testDataDir, "encryption_dict_handler.yml")
        with open(cls.testDataDir, "r") as f:
            cls.testData = yaml.safe_load(f)
        cls.password = "8B62D98CB4BCE07F896EC6F30A146E00"

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
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

    def test_text_encrpyt(self, *args, **kwargs):
        decrypted, length = "Hello World!", 94
        encrypted = handler.text_encrypt(decrypted, self.password)
        self.assertNotEqual(decrypted, encrypted)
        self.assertNotIn(decrypted, encrypted)
        self.assertEqual(length, len(encrypted))

    def test_text_decrypt(self, *args, **kwargs):
        encrypted = """
                    VMVxRPoG9+qAOlyvJCKj3U/GZlgYIC9GQzanpAsTsow=:ExucUB7YAft+CFlZn+lJSw==
                    :FZiDZkGihg8WNeCzRmxHmg==
                    """.replace(
            " ", ""
        ).replace(
            "\n", ""
        )
        decrypted = handler.text_decrypt(encrypted, self.password)
        self.assertNotEqual(decrypted, encrypted)
        self.assertEqual(decrypted, "Hello World!")

    def test_dict_encrypt(self, *args, **kwargs):
        encrypted = handler.dict_encrypt(self.testData, self.password)

    def test_dict_decrypt(self, *args, **kwargs):
        encrypted = """
                    06nQNI425/p2osgZ11IUr0XYSNbyvZe2uyOWdAQ1+Ag=:VYw1b4C5gIFUlDh4AQBZMg==:
                    5b4lA8QfqgxvBfH2h80f0gRGSMoy32JvIkPJp6w6tMvTb/Dh/Sfqhh4ZeKA6tiejbzuKxP
                    9ZKwqxCEYMRDSGQBPFudafbHLr0gHvrsmN2dVjsviMskLUp+Hk0NvdVS5S2uG6WJUbvtxf
                    EuF5Pop4+2u5lyeO56isYnuorR+0EVpZJwN91XFFkxU+RNP0cJ3VMbC2+Tg22CD/uhn2C+
                    ARYzTXQ7TZlYViojC94UknJK8os6vyMUKRAQS26JqDVUGIF8nnoC5yhlFCrxU7Irljeo+4
                    OIiPqiOkLTUZgiPmciXJQ+xDi04P03MjMhGSnjgR
                    """.replace(
            " ", ""
        ).replace(
            "\n", ""
        )
        decrypted = handler.dict_decrypt(encrypted, self.password)
        self.assertEqual(decrypted, self.testData)


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
