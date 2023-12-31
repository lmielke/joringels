# standard lib imports
import colorama as color

color.init()
from contextlib import contextmanager
import os, re, shutil, sys, time
import yaml
import unittest

# C:\Users\lars\python_venvs\libs\joringels\joringels\test\test_api_handler.py
# test package imports
import joringels.src.settings as sts
import joringels.src.helpers as helpers
import joringels.src.data as data
import joringels.src.get_soc as soc

# print(f"\n__file__: {__file__}")


class Test_ClusterParams(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        cls.tempDirName = "temp_test_data"
        cls.tempDataDir = helpers.mk_test_dir(cls.tempDirName)
        cls.safeName = "safe_one"
        cls.regex = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        cls.params = {
            "safeName": cls.safeName,
            "productName": "haimdall",
            "clusterName": "testing",
            "key": sts.testKeyOuter,
            "keyV": sts.testKeyInner,
            # never remove retain, it will break the test
            "retain": True,
        }
        cls.deletePaths = []

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        helpers.rm_test_dir(cls.tempDataDir)
        try:
            for path in cls.deletePaths:
                if os.path.exists(path):
                    os.remove(path)
        except:
            pass

    def test_update(self):
        # first initialize the class with the default settings
        newHost = "123.234.345.6"
        clParams = data.ClusterParams()
        self.assertTrue(re.search(self.regex, clParams.secureHosts[0]))
        self.assertEqual(clParams.host, soc.get_local_ip())
        # now update two one field using update method
        kwargs = {"host": newHost}
        clParams.update(kwargs)
        # host field is changed because its in kwars
        self.assertEqual(clParams.host, newHost)
        # port remains unchanged
        self.assertEqual(clParams.port, sts.defaultPort)


class Test_DataSafe(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 1
        cls.tempDirName = "temp_test_data"
        cls.tempDataDir = helpers.mk_test_dir(cls.tempDirName)
        cls.safeName = "safe_one"
        cls.regex = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        cls.params = {
            "safeName": cls.safeName,
            "productName": "haimdall",
            "clusterName": "testing",
            "key": sts.testKeyOuter,
            "keyV": sts.testKeyInner,
            # never remove retain, it will break the test
            "retain": True,
        }
        cls.deletePaths = []

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        helpers.rm_test_dir(cls.tempDataDir)
        try:
            for path in cls.deletePaths:
                if os.path.exists(path):
                    os.remove(path)
        except:
            pass

    def test_source_kdbx(self):
        # Example data in a kwargs dictionary
        kwargs = helpers.load_yml(os.path.join(sts.testDataDir, "#safe_one.yml")).get("safe_one")
        # Instantiate the data.DataSafe class using the kwargs dictionary
        ds = data.DataSafe.source_kdbx(kwargs)
        # Assertions to verify that the instance is created correctly
        self.assertEqual(ds.safeName, "safe_one")
        self.assertEqual(ds.dataKey, "myDataKey")
        self.assertEqual(ds.dataSafeKey, "testing")
        self.assertEqual(ds.entries[0], "python_venvs/databases/aws_postgres")


if __name__ == "__main__":
    with helpers.temp_password(pw=sts.testKeyOuter):
        unittest.main()
