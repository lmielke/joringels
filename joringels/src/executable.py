import os, re, sys, time
import joringels.src.settings as sts


class Executable:
    def __init__(self, packageDir, *args, **kwargs):
        self.kill = False
        self.msg = []
        self.packageDir = sts.unalias_path(packageDir)
        self.projectName = os.path.basename(packageDir)
        self.path = self.get_exec_path(*args, **kwargs)
        self.source = "python"

    def get_exec_path(self, *args, execsDir=sts.execsDir, **kwargs):
        """
        looks in various possible locations for the executable
        locations can be either the package directory itself or the ouside
        package Pipenv standard location
        """
        executables = []
        # first look inside the package directory
        venvFile = os.path.join(self.packageDir, ".venv")
        if os.path.exists(venvFile):
            with open(venvFile, "r") as v:
                executable = v.read().strip()
                if os.path.exists(executable):
                    return executable.replace("/", os.sep)
        # if executable exists outside of package, get it from there
        execsDir = os.path.normpath(os.path.expanduser(execsDir))
        execs = [ex for ex in os.listdir(execsDir) if ex.startswith(self.projectName)]
        if self.check_executables(execs, execsDir, *args, **kwargs):
            return os.path.normpath(os.path.join(execsDir, execs[0], "Scripts", "python.exe"))
        return False

    def check_executables(self, execs, execsDir, *args, **kwargs):
        if len(execs) == 0:
            self.msg.append(f"No executalbe found for {self.projectName}")
            self.kill = True
        elif len(execs) == 1:
            return True
        elif len(execs) >= 2:
            self.msg.append(f"{self.projectName} test found mulitple envs {execs}")
            self.kill = True
        return False

    def run_subprocess(self, packageDir, testMethods, paths, kill, *args, **kwargs):
        """
        runs the test using subprocess.Popen
        """
        # run test cmds
        return (
            subprocess.Popen(
                ["echo", "Testopia ERROR:"]
                if kill or self.kill
                else [self.source, paths.testFilePath, *testMethods],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=packageDir,
                executable=self.path,
            ),
            True,
        )
