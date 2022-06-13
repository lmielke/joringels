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

    def main(self, *args, **kwargs):
        with sts.temp_chdir(sts.appBasePath):
            cmds = ["python", "-m", "unittest"]
            results = (
                subprocess.Popen(cmds, stderr=subprocess.PIPE, executable=sys.executable)
                .stderr.read()
                .decode("utf-8")
            )
            results = "\n".join(
                [l for l in results.replace("\r", "").replace("\n\n", "\n").split("\n")]
            )
            self.log.info(f"\n{results}")
            for l in results.split("\n"):
                print(l)


if __name__ == "__main__":
    UnitTestWithLogging().main()
