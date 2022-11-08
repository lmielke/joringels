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

# jo upload -n timesheet_testing -src kdbx -con scp -pr all
class UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        # cls.testData = cls.get_test_data(*args, **kwargs)
        cls.creds = {'entryName': sts.clusters_params, 'safeName': 'timesheet_testing'}

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def get_test_data(cls, *args, **kwargs):
        with open(os.path.join(sts.testDataPath, 'test_tempfile.yml'), 'r') as f:
            return yaml.safe_load(f)

    def test_temp_secret(self, *args, **kwargs):
        expected = ['_apis', '_joringels']
        # filePth has to be full path to tempfile.yml or .json
        filePath = os.path.join(sts.testDataPath, 'temp_secret.yml')
        with tempfile.temp_secret(
                                    *args,
                                    secretsFilePath=filePath,
                                    creds=self.creds,
                                    **kwargs
                                    ) as t:
            with open(filePath, 'r') as f:
                content = list(yaml.safe_load(f).keys())[:2]
        self.assertEqual(content, expected)
        

if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
