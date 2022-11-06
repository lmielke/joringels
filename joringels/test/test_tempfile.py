# standard lib imports
import colorama as color

color.init()

import os, re, shutil, sys, time
import yaml
import unittest
# C:\Users\lars\python_venvs\libs\joringels\joringels\test\test_tempfile.py
# test package imports
import joringels.src.settings as sts
from joringels.src.actions import tempfile

# print(f"\n__file__: {__file__}")


class UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        # cls.testData = cls.get_test_data(*args, **kwargs)
        cls.creds = {'entryName': '_joringels.yml', 'safeName': 'digiserver'}

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def get_test_data(cls, *args, **kwargs):
        with open(os.path.join(sts.testDataPath, 'test_tempfile.yml'), 'r') as f:
            return yaml.safe_load(f)

    def test_temp_secret(self, *args, **kwargs):
        expected = 'digiserver'
        # filePth has to be full path to tempfile.yml or .json
        filePath = os.path.join(sts.testDataPath, 'temp_secret.yml')
        with tempfile.temp_secret(
                                    *args,
                                    secretsFilePath=filePath,
                                    creds=self.creds,
                                    **kwargs
                                    ) as t:
            with open(filePath, 'r') as f:
                content = yaml.safe_load(f).get('DATASAFENAME')
        self.assertEqual(content, expected)
        

if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
