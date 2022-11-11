# test_unittest.py

from datetime import datetime as dt
import os, re, sys
import subprocess

import joringels.src.settings as sts
import joringels.src.logger as logger


class UnitTestWithLogging:
    def __init__(self, *args, **kwargs):
        self.timeStamp = re.sub(r"([:. ])", r"-", str(dt.now()))
        self.logDir = os.path.join(sts.testPath, "logs")
        assert os.path.isdir(self.logDir), f"logDir: {self.logDir} does not exist !"
        self.logDefaultName = f"{os.path.basename(__file__)[:-3]}_{self.timeStamp}.log"
        self.log = logger.mk_logger(self.logDir, self.logDefaultName, __name__)

    def run_unittest(self, *args, **kwargs):
        with sts.temp_chdir(sts.appBasePath):
            cmds = ["python", "-m", "unittest"]
            results = (
                subprocess.Popen(cmds, stderr=subprocess.PIPE, executable=sys.executable)
                .stderr.read()
                .decode("utf-8")
            )
            summary = self.extract_stats(results)
            results = "\n".join(
                [l for l in results.replace("\r", "").replace("\n\n", "\n").split("\n")]
            )
            self.log.info(f"{summary}\n{results}")
            print(f"logged results in : {self.logDir}")

    def extract_stats(self, results):
        """ summerizes test results to add to the log header like [all:12 ok:11 err:1]
            NOTE: the log header is read by powershell, so treat with care
        """
        regex = r'(Ran )(\d{1,3})( tests in .*)'
        match = re.search(regex, results)
        # tet total number of tests
        if match:
            numTests = match.group(2)
            if numTests.isnumeric():
                numTests = int(numTests)
        # get fails
        if 'OK' in results:
            numFails = 0
        elif 'FAILED' in results:
            errRegex = r'(FAILED \(failures=)(\d{1,3})\)'
            errMatch = re.search(errRegex, results)
            if match:
                numFails = errMatch.group(2)
                if numFails.isnumeric():
                    numFails = int(numFails)
        numOk = numTests - numFails
        return f"summary: [all:{numTests} ok:{numOk} err:{numFails}]"


def main(*args, **kwargs):
    UnitTestWithLogging().run_unittest()


if __name__ == "__main__":
    main()
