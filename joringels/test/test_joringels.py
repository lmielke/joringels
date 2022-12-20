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
from joringels.src.joringels import Joringel
from joringels.src.encryption_dict_handler import dict_decrypt
from joringels.src.encryption_dict_handler import dict_values_decrypt
from logunittest.settings import testLogsDir

# print(f"\n__file__: {__file__}")


class UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.testData = cls.get_test_data(*args, **kwargs)
        cls.mk_test_logs_dir(*args, **kwargs)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def get_test_data(cls, *args, **kwargs):
        with open(os.path.join(sts.testDataDir, "test_api_handler.yml"), "r") as f:
            return yaml.safe_load(f)

    @classmethod
    def mk_test_logs_dir(cls, *args, **kwargs):
        logDir = os.path.join(testLogsDir, 'joringels')
        if not os.path.exists(logDir):
            os.makedirs(logDir)

    def test__memorize(self, *args, **kwargs):
        expected = [sts.apiParamsFileName, "apiEndpointDir", 'logunittest']
        testData = self.testData
        testData["apiEndpointDir"] = sts.appBasePath
        j = Joringel(*args, **kwargs)
        encrypted = j._memorize(
            *args, safeName="safe_one", secrets=self.testData, connector="joringels", **kwargs
        )
        decrypted = dict_decrypt(encrypted)
        self.assertEqual(list(decrypted.keys()), expected)

    def test__digest(self, *args, **kwargs):
        one = f'{sts.testDataDir}/safe_one.yml'.replace(os.sep, '/')
        two = 'haimdall'
        three = {'action': 'send', 'import': 'haimdall.actions.communicate', 'response': None}
        os.environ['secrets'] = os.path.join(sts.testDataDir, 'joringels.kdbx')
        sts.encryptDir = sts.testDataDir
        apiName = 'haimdall'
        clusterName = 'testing_cluster'
        kwargs = {  
                        'safeName':'safe_one',
                        'productName': apiName,
                        'clusterName': clusterName,
                        'key':'testing',
                        # never remove retain, it will break the test
                        'retain': True,
                        }
        j = Joringel(**kwargs)
        encryptPath, secrets = j._digest(*args, **kwargs )
        self.assertEqual(one, encryptPath.replace(os.sep, '/'))
        self.assertEqual(two, secrets.get('PRODUCTNAME'))
        # apiParams are found in a nested dictionary using integer values to ref api params
        # so [0] here is a dict parameter
        self.assertEqual(three, secrets[clusterName]['cluster_params']['services'][apiName][0])
        # apiParams are also stored in j.api dictionary in encrypted form
        # hence ['0'] here is identical to [0] in apiParams select above
        self.assertEqual(   secrets[clusterName]['cluster_params']['services'][apiName][0],
                                    dict_values_decrypt(dict_decrypt(j.api))[apiName]['0']
                        )

    def test__from_memory(self, *args, **kwargs):
        # entry spells: _apis
        validEntry = (
            f"o6Xf0DsT8I+rHnN0ohMLCNibazPyhctEgrCzyArw2PQ=:"
            f"ToRtnoI127Ld0au8MwVjBQ==:oJ0sr3gmq/sGkXDwUXmunQ=="
        )
        # entry spells: Hello World!
        inValidEntry = (
            f"x4Y92RtoC1Zh/JW3++iNdu62XK89zHr/2GE0hn8Ry+g=:"
            f"mUlKDMKRTmYk98wzUUFg9w==:yVKM1uhtWsoK3YfxRzlX3g=="
        )
        with temp_password(pw="8B62D98CB4BCE07F896EC6F30A146E00") as t:
            j = Joringel(*args, **kwargs)
            with open(os.path.join(sts.testDataDir, "test_from_memory.txt"), "r") as f:
                j.secrets = f.read()
            self.assertIsNotNone(j._from_memory(validEntry))
            self.assertIsNone(j._from_memory(inValidEntry))

    def test__handle_integer_keys(self, *args, **kwargs):
        data = {"1": "one", "two": "two", 3: "three", "3.14": "something"}
        expected = [1, "two", 3, "3.14"]
        j = Joringel(*args, **kwargs)
        corrected = j._handle_integer_keys(data)
        self.assertEqual(list(corrected.keys()), expected)

    def test__get_recent_logfile(self, *args, **kwargs):
        j = Joringel(*args, **kwargs)
        text = j._get_recent_logfile(connector='joringels')
        self.assertIn("INFO logunittest - run_unittest", text)


from contextlib import contextmanager


@contextmanager
def temp_password(*args, pw, **kwargs) -> None:
    current = os.environ["DATASAFEKEY"]
    try:
        os.environ["DATASAFEKEY"] = pw
        yield
    finally:
        os.environ["DATASAFEKEY"] = current


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
