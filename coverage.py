# stats.py

import os, re, sys


class UnitTestStats:
    """ gets unittest stats from logfile and returns it as a parsable string
        output can be used to display test status
        NOTE: this module is used by powershell to display test result in header
        HANDLE WITH CARE
    """
    def __init__(self, *args, **kwaargs):
        self.logDir = self.get_log_dir()


    def get_log_dir(self):
        projectKeyFile, packageKeyFile = 'setup.cfg', '__main__.py'
        files = os.listdir()
        if not projectKeyFile in files and not packageKeyFile in files:
            return None
        elif projectKeyFile in files:
            logDir = os.path.join(os.getcwd(), 'joringels', 'test', "logs")
        elif packageKeyFile in files:
            logDir = os.path.join(os.getcwd(), 'test', "logs")
        return logDir

    def get_logfile_summary(self):
        if self.logDir is None:
            sys.stderr.write(f"<@><{dt.today()}>!{'logdir not found'}<@>")
        logFile = self.get_recent_logfile()
        regex = r'([0-9 :-]*)( INFO logunittest - run_unittest: summary: )(\[.*\])'
        with open(logFile, 'r') as text:
            match = re.search(regex, text.read())
        if match:
            time = match.group(1)
            testResults = match.group(3)
        sys.stderr.write(f"<@><{time}>!{testResults}<@>")


    def get_recent_logfile(self):
        files = ([os.path.join(self.logDir, f) for f in os.listdir(self.logDir)
                                             if os.path.isfile(os.path.join(self.logDir, f))])
        latest = max(files, key=os.path.getctime)
        return latest

    def main(self, *args, **kwargs):
        return self.get_logfile_summary()

if __name__ == "__main__":
    UnitTestStats().main()
