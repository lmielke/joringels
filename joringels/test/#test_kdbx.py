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
from joringels.src.joringels import Joringel

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
            "keykdbx": "testing",
            "key": sts.testKeyOuter,
            "keyV": sts.testKeyInner,
        }
        cls.KP = kdbx.KeePassSecrets("load", *args, **cls.kwargs)
        # cls.KP.mk_session(*args, **cls.kwargs)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def get_test_data(cls, *args, **kwargs):
        with open(os.path.join(sts.testDataDir, "test_api_handler.yml"), "r") as f:
            return yaml.safe_load(f)

    def test_read_safe_data(self, *args, **kwargs):
        self.KP.read_safe_data(*args, **kwargs)
        self.assertTrue(self.KP.dataSafe is not None)
        self.assertTrue(self.KP.dataSafe.title == self.safeName)

    def test_read_cluster_data(self, *args, **kwargs):
        self.KP.read_cluster_data(*args, **kwargs)
        self.assertTrue(self.KP.cluster is not None)
        self.assertTrue(self.KP.cluster.title == self.clusterName)

    def test_read_source(self, *args, **kwargs):
        self.KP.read_source(*args, **kwargs)
        self.assertTrue(self.KP.cluster is not None)
        self.assertTrue(self.KP.cluster.title == self.clusterName)

    def test_get_entry(self, *args, **kwargs):
        dataSafe = self.KP.get_entry(
            entryName=self.kwargs["safeName"], groupName=sts.dataSafeGroup
        )
        self.assertEqual(dataSafe.title, self.kwargs["safeName"])
        # run the test to get cluster
        cluster = self.KP.get_entry(
            entryName=self.kwargs["clusterName"], groupName=self.kwargs["productName"]
        )
        self.assertEqual(cluster.title, self.kwargs["clusterName"])

    def test_parse_entry(self, *args, **kwargs):
        entry = self.KP.parse_entry(entryName=self.kwargs["safeName"], groupName=sts.dataSafeGroup)
        self.assertEqual(entry.title, self.kwargs["safeName"])

    def test_read_source(self, *args, **kwargs):
        secrets = self.KP.read_source()

    def test_get_source(self, *args, **kwargs):
        secretsPath = self.KP.get_source(*args, **self.kwargs)
        self.assertEqual(secretsPath, os.environ.get("secrets"))

    def test_get_creds(self, *args, **kwargs):
        testCreds = "testing"
        creds = self.KP.get_creds(*args, key=testCreds)
        self.assertEqual(creds, testCreds)

    def test__enter__(self, *args, **kwargs):
        j = Joringel(*args, **self.kwargs)
        # get secret
        with kdbx.KeePassSecrets("load", *args, **self.kwargs) as src:
            secrets = src.read_source(*args, **self.kwargs)
            j.create(j.encryptPath, secrets, *args, **kwargs)


if __name__ == "__main__":
    with helpers.temp_password(pw=sts.testKeyOuter):
        unittest.main()
    print("done")
    exit()
