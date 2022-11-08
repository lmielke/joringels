# standard lib imports
import colorama as color

color.init()

import os, re, shutil, sys, time
import yaml
import unittest
# C:\Users\lars\python_venvs\libs\joringels\joringels\test\test_upload.py
# test package imports
import joringels.src.settings as sts
from joringels.src.actions import upload

# print(f"\n__file__: {__file__}")


class UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.testData = cls.get_test_data(*args, **kwargs)
        cls.encryptPath = r'C:\Users\lars\.ssp\timesheet_testing.yml'
        # self.upload = upload.main(*args, **cls.testData['kwargs'])

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def get_test_data(cls, *args, **kwargs):
        with open(os.path.join(sts.testDataPath, 'test_upload.yml'), 'r') as f:
            return yaml.safe_load(f)

    def test_get_targets(self, *args, **kwargs):
        expected_names = ['joringels','oamailer']
        expected_targets = (
                            'python_venvs/000_provider/apps/joringels/joringels-pwd-user',
                            'python_venvs/000_provider/apps/oamailer/oamailer-pwd-user'
                            )
        targetNames, targets = upload.get_targets(self.testData['secrets'], *args, **self.testData['kwargs'])
        self.assertEqual(targetNames, expected_names)
        self.assertEqual(targets[0], self.testData['secrets']['joringels-pwd-user'])


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
