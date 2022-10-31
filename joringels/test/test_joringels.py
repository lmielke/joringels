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
        testData = self.testData
        testData['apiEndpointDir'] = 'C:\\Users\\lars\\python_venvs\\modules\\oamailer'
        j = Joringel(*args, **kwargs)
        j._memorize(*args, safeName='oamailer', secrets=self.testData, **kwargs)
        self.assertEqual(j.host, self.testData['kwargs'].get('host'))
        self.assertEqual(j.port, self.testData['kwargs'].get('port'))
        self.assertEqual(j.contentType, self.testData['kwargs'].get('contentType'))

if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
