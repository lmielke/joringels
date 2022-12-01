# standard lib imports
import colorama as color

color.init()

import os, re, shutil, sys, time
import yaml
import unittest

# C:\Users\lars\python_venvs\libs\joringels\joringels\test\test_api_handler.py
# test package imports
import joringels.src.settings as sts
import joringels.src.helpers as helpers
import os

# print(f"\n__file__: {__file__}")


class UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        # cls.testData = cls.get_test_data(*args, **kwargs)
        cls.safeName = 'safe_one'
        cls.productName = 'haimdall'
        cls.clusterName = 'testing_cluster'
        cls.exportDir = os.path.join(sts.testDataDir, 'actions')
        os.environ['secrets'] = os.path.join(sts.testDataDir, 'joringels.kdbx')
        sts.encryptDir = sts.testDataDir
        cls.kwargs = {  
                        'safeName':cls.safeName,
                        'entryName': 'safe_one',
                        'productName':cls.productName,
                        'clusterName':cls.clusterName,
                        'key': 'testing',
                        'retain': True,
                        }

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    # @classmethod
    # def get_test_data(cls, *args, **kwargs):
    #     with open(os.path.join(sts.testDataDir, "test_api_handler.yml"), "r") as f:
    #         return yaml.safe_load(f)

    def test_fetch(self, *args, **kwargs):
        from joringels.src.actions import fetch
        out = fetch.alloc(*[], **self.kwargs)
        self.assertEqual('myDataSafeKey', out.get('password'))
        

    def test_load(self, *args, **kwargs):
        pass
        # self.assertEqual('adminUser', postgresUser)


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
