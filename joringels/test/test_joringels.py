# standard lib imports
import colorama as color

color.init()

import os, re, shutil, sys, time
import yaml
import unittest
# C:\Users\lars\python_venvs\libs\joringels\joringels\test\test_api_handler.py
# test package imports
import joringels.src.settings as sts
from joringels.src.joringels import Joringel
from joringels.src.encryption_dict_handler import text_decrypt, text_encrypt, dict_encrypt, dict_decrypt, dict_values_decrypt, dict_values_encrypt


# print(f"\n__file__: {__file__}")


class UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.testData = cls.get_test_data(*args, **kwargs)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def get_test_data(cls, *args, **kwargs):
        with open(os.path.join(sts.testDataPath, 'test_api_handler.yml'), 'r') as f:
            return yaml.safe_load(f)

    def test__memorize(self, *args, **kwargs):
        expected = ['_apis', 'apiEndpointDir']
        testData = self.testData
        testData['apiEndpointDir'] = 'C:\\Users\\lars\\python_venvs\\modules\\oamailer'
        j = Joringel(*args, **kwargs)
        encrypted = j._memorize(    
                                *args,
                                safeName='digiserver',
                                secrets=self.testData,
                                connector='oamailer', **kwargs
                                )
        decrypted = dict_decrypt(encrypted)
        self.assertEqual(list(decrypted.keys()), expected)

    def test__handle_integer_keys(self, *args, **kwargs):
        data = {'1': 'one', 'two': 'two', 3: 'three'}
        expected = [1, 'two', 3]
        j = Joringel(*args, **kwargs)
        corrected = j._handle_integer_keys(data)
        self.assertEqual(list(corrected.keys()), expected)

if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
