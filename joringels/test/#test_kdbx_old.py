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
from joringels.src.sources import kdbx

# print(f"\n__file__: {__file__}")


class Test_KeePassSecrets(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.testData = cls.get_test_data(*args, **kwargs)
        cls.safeName = "safe_one"
        cls.productName = "haimdall"
        cls.clusterName = "testing_cluster"
        os.environ["secrets"] = os.path.join(sts.testDataDir, "joringels.kdbx")
        sts.encryptDir = sts.testDataDir
        cls.kwargs = {
            "safeName": cls.safeName,
            "productName": cls.productName,
            "clusterName": cls.clusterName,
            "key": sts.testKeyOuter,
            "keyV": sts.testKeyInner,
        }
        cls.KP = kdbx.KeePassSecrets("load", *args, **cls.kwargs)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def get_test_data(cls, *args, **kwargs):
        with open(os.path.join(sts.testDataDir, "test_api_handler.yml"), "r") as f:
            return yaml.safe_load(f)

    def test__init__(self, *args, **kwargs):
        # targets
        self.assertEqual(
            {
                "haimdall_server": "python_venvs/physical_machines",
                "joringels_server": "python_venvs/physical_machines",
            },
            self.KP.targets,
        )
        # entreis
        self.assertEqual(
            ["python_venvs/databases/aws_postgres", "python_venvs/data_safes/safe_one"],
            self.KP.entries[:2],
        )

    def test_load(self, *args, **kwargs):
        self.KP.load(*args, **self.kwargs)
        postgresUser = self.KP.secrets.get("aws_postgres").get("username")
        self.assertEqual("adminUser", postgresUser)


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
