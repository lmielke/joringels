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
from joringels.src.encryption_dict_handler import (
    text_decrypt,
    text_encrypt,
    dict_decrypt,
    dict_encrypt,
    dict_keys_encrypt,
    dict_keys_decrypt,
    dict_values_decrypt,
    dict_values_encrypt,
)


# print(f"\n__file__: {__file__}")


class Test_UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.prep_enc_path(*args, **kwargs)
        cls.testDataDir = os.path.join(sts.testDataDir, "encryption_dict_handler.yml")
        with open(cls.testDataDir, "r") as f:
            cls.testData = yaml.safe_load(f)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        if os.path.exists(cls.encryptPath):
            os.remove(cls.encryptPath)

    @classmethod
    def prep_enc_path(cls, *args, **kwargs):
        cls.encryptPath = os.path.join(sts.testDataDir, "safe_one.yml")
        if os.path.exists(cls.encryptPath):
            return True

    def test_dict_encrypt(self, *args, **kwargs):
        encrypted = dict_encrypt(sts.testDataDict, key=sts.testKeyOuter, keyV=sts.testKeyInner)
        self.assertNotEqual(encrypted, sts.testDataDict)
        self.assertTrue(len(encrypted) >= len(str(sts.testDataDict)) and not " " in encrypted)

    def test_dict_decrypt(self, *args, **kwargs):
        encrypted = sts.cryptonizeDataStr
        decrypted = dict_decrypt(encrypted, key=sts.testKeyOuter, keyV=sts.testKeyInner)
        self.assertEqual(decrypted, sts.testDataDict)

    def test_text_encrpyt(self, *args, **kwargs):
        decrypted, length = "Hello World!", 94
        encrypted = text_encrypt(decrypted, sts.testKeyInner)
        self.assertNotEqual(decrypted, encrypted)
        self.assertNotIn(decrypted, encrypted)
        self.assertEqual(length, len(encrypted))

    def test_text_decrypt(self, *args, **kwargs):
        encrypted = (
            f"xTR83GcikFeXAUhzIBWrswFsDqLxUIFPc/azocBqV1w=:yoiQxBRuRNwrhPTqdx/fCA==:"
            f"7X1c6iBoZslzZcqytJwHcQ=="
        )
        decrypted = text_decrypt(encrypted, sts.testKeyInner)
        self.assertNotEqual(decrypted, encrypted)
        self.assertEqual(decrypted, "Hello World!")

    def test_dict_values_encrypt(self, *args, **kwargs):
        encrypted = dict_values_encrypt(self.testData, sts.testKeyInner)
        # the following test should raise valueError
        self.assertEqual(
            self.testData["encryption_dict_handler"]["lavel_1_key_1"], "level_1_value_1"
        )
        with self.assertRaises(TypeError) as context:
            # keys should not yet be encrypted
            self.assertEqual(encrypted.keys(), self.testData.keys())
            # values should be encrypted
            self.assertEqual(
                encrypted["encryption_dict_handler"]["lavel_1_key_1"], "level_1_value_1"
            )
        decrypted = dict_values_decrypt(encrypted, sts.testKeyInner)
        self.assertEqual(decrypted, self.testData)

    def test_dict_keys_decrypt(self, *args, **kwargs):
        # to regenerate encrypted uncomment below
        # print(dict_encrypt(self.testData, key=sts.testKeyOuter, keyV=sts.testKeyInner))
        encrypted = (
            f"IRKVeqr+0yCI5Cy1pH007vp2iZQyo+N719+FF+FR6kg=:yLBlNqd60/y2oIU4yCxgBg==:"
            f"K+22bfVKHezAFY2YpKooGmTj1KUzDHQfnzfvr0Qcdeq5J6LgRQCULAAsCHqcSb1MdMqmir"
            f"lLNzhKcT2nkcpKDgx+7loPoLNuhn2oxRICxpWH04/tS0UKZJfgBEheuxMeJqQAxOkTHfpX"
            f"KcPArasGZDztAAUiI18zzwl40wxhGqriJYW/A27bXatXdyzrGxrA7IBFWNspdV0iZ6alvy"
            f"PwjggWFFfZWKf3JSmuOpnRPAZ26z7ZBmRwjpmO+ImOgKyVdY04RhmW6EP3M2Bl2tA6rjdK"
            f"C+ik02Ms7FbJuzbb9LcvXMSAU7tWa3IAnDleda9vn/+t6tI3JrLos8cn7wIjeb6Ra86l8N"
            f"q8IZQ9ouTd5RMjW02YHj06wcUlTdUZdxkje2iGsESGiEOFvxV31gQTWhMRhzpngcgU+Y1n"
            f"/ouwZ+jcBGSxmy/b6WFrqQzcbwhXHIvj5HxsezsFBpBI5vk/gA=="
        )
        decrypted = dict_decrypt(encrypted, key=sts.testKeyOuter, keyV=sts.testKeyInner)
        self.assertEqual(decrypted, self.testData)


if __name__ == "__main__":
    with helpers.temp_password(pw=sts.testKeyOuter):
        unittest.main()
