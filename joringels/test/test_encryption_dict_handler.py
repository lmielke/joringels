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

    def test_text_encrpyt(self, *args, **kwargs):
        decrypted, length = "Hello World!", 94
        encrypted = text_encrypt(decrypted, sts.testKey)
        self.assertNotEqual(decrypted, encrypted)
        self.assertNotIn(decrypted, encrypted)
        self.assertEqual(length, len(encrypted))

    def test_text_decrypt(self, *args, **kwargs):
        encrypted = (
            f"iUhrFVZaKgwKqE0PaUM2xW6i64465e6WX8DUKCLoG8c=:seEPTkYYnxWYtU+hsUx0Kw==:"
            f"WumOPbNkIQXC8eFwb9kWDw=="
        )
        decrypted = text_decrypt(encrypted, sts.testKey)
        self.assertNotEqual(decrypted, encrypted)
        self.assertEqual(decrypted, "Hello World!")

    def test_dict_values_encrypt(self, *args, **kwargs):
        encrypted = dict_values_encrypt(self.testData, sts.testKey)
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
        decrypted = dict_values_decrypt(encrypted, sts.testKey)
        self.assertEqual(decrypted, self.testData)

    def test_dict_keys_decrypt(self, *args, **kwargs):
        encrypted = (
            f"lOp+GJI+5mAXs03ltOhMGxR0d9OxZKoEYG4bUxZgxbA=:63BtEJFHiz6RUgDwoMezzg==:"
            f"y6+nvxJLreZYjZGnXy2Bm72xnLYZHibQyIqTEobNnWVCrdsriEPubcQRojmcwdaRWgid3s"
            f"Dj08eQjKj71wdUxdADBrhkA6yU5H/WqfY/vNTwWmFSJ6Yl+FiLtv2vq1NQJ2FtF4TZFjGy"
            f"MXWlX2zUIMe7LRZtjB+jZH5WG0GeDibgqOalzUvhLAhl4BhjZusNezW7nO59J/QcnZYFg+"
            f"aFOIHEn7DvmYMtpBu/QUleZ6tU81ngi/1lrIfU7vPzXOOfGnTqDG/s12VAvPjS2JW23ivG"
            f"dzpwykNJr6UL+XGB9HJXoBSZlZeZpavUjxJSWI8N5g+m8le8VRhp/TLy3prbvsn+EbTrgx"
            f"9mwS8wBzHkS2iClOBFbAXrEekXmsUzLlsJ7pZ6IiS3QFLooKBN4ZUkTU0nBOOvLvhsasWW"
            f"5ec18FKRKOqc5OyEsAQzYL+jpED5sbp4zCpoqCP0tmjXFzzvTQ=="
        )
        decrypted = dict_decrypt(encrypted, key=sts.testKey, keyV=sts.testKey)
        self.assertEqual(decrypted, self.testData)


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
