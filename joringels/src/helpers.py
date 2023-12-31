# helpers.py
from pathlib import Path
import json, os, shutil, sys, time, yaml
from contextlib import contextmanager
import joringels.src.settings as sts
import functools


def unalias_path(workPath: str) -> str:
    """
    repplaces path aliasse such as . ~ with path text
    """
    if not any([e in workPath for e in [".", "~", "%"]]):
        return workPath
    workPath = workPath.replace(r"%USERPROFILE%", "~")
    workPath = workPath.replace("~", os.path.expanduser("~"))
    if workPath.startswith(".."):
        workPath = os.path.join(os.path.dirname(os.getcwd()), workPath[3:])
    elif workPath.startswith("."):
        workPath = os.path.join(os.getcwd(), workPath[2:])
    workPath = os.path.normpath(os.path.abspath(workPath))
    return workPath


def prep_path(workPath: str, filePrefix=None) -> str:
    workPath = unalias_path(workPath)
    if os.path.exists(workPath):
        return workPath
    # check for extensions
    extensions = ["", sts.eext, sts.fext]
    name, extension = os.path.splitext(os.path.basename(workPath))
    for ext in extensions:
        workPath = unalias_path(f"{name}{ext}")
        if os.path.isfile(workPath):
            return workPath
    return f"{name}{extension}"


def get_dict_entry(d, matcher, ret="key", current_key=None) -> str:
    if isinstance(d, dict):
        for key, value in d.items():
            if key == matcher:
                return current_key if ret == "key" else d[key]
            elif isinstance(value, dict):
                result = get_dict_entry(value, matcher, ret, current_key=key)
                if result is not None:
                    return result
    return None


def mk_encrypt_path(safeName: str) -> str:
    encrpytPath = os.path.join(
        sts.encryptDir,
        safeName.lower() if safeName.endswith(sts.eext) else f"{safeName.lower()}{sts.eext}",
    )
    decryptPath = os.path.join(
        sts.encryptDir,
        safeName.lower() if safeName.endswith(sts.fext) else f"{safeName.lower()}{sts.fext}",
    )
    return encrpytPath, decryptPath


def data_safe_files(*args, safeName=None, **kwargs) -> list:
    """takes a name and checks if its a fileName or dirName
    then returns all files belongin to that file, dir
    i.e. chkey can change one dataSafe key or keys of all dataSafes in dir
    """
    if safeName is None:
        return [
            os.path.join(sts.encryptDir, f)
            for f in os.listdir(sts.encryptDir)
            if f.endswith(sts.eext)
        ]
    else:
        return [os.path.join(sts.encryptDir, f"{safeName}{sts.eext}")]


@contextmanager
def temp_secret(j, *args, secretsFilePath: str, entryName: str, **kwargs) -> None:
    """
    temporaryly renames files in .ssp for upload to bypass files
    secretsFilePath: full path to secretsfile.json
    creds: joringels params to get secret
            {entryName: secretToWrite}
    """
    fType = os.path.splitext(secretsFilePath)[-1]
    try:
        secrets = j.secrets.get(entryName)
        with open(secretsFilePath, "w") as f:
            if fType == ".json":
                json.dump(secrets, f)
            elif fType == "sts.fext":
                yaml.dump(secrets, f)
            else:
                raise Exception(f"Invalid file extension: {fType}, use [.json, sts.fext]")
        while not os.path.exists(secretsFilePath):
            continue
        yield
    except Exception as e:
        print(f"oamailer.secrets_loader Exception: {e}")
    finally:
        if os.path.exists(secretsFilePath):
            os.remove(secretsFilePath)


@contextmanager
def temp_chdir(path: Path, *args) -> None:
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """

    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


@contextmanager
def temp_ch_host_name(hostName: str) -> None:
    """Sets the cwd within the context
    Args:
        host (Path): The host to the cwd
    Yields:
        None
    """
    origin = os.environ.get("HOSTNAME", "")
    try:
        os.environ["HOSTNAME"] = hostName
        yield
    finally:
        os.environ["HOSTNAME"] = origin


@contextmanager
def temp_safe_rename(*args, safeName: str, prefix: str = "#", **kwargs) -> None:
    """
    temporaryly renames files in .ssp for upload to bypass files
    """
    # rename fileName by adding prefix
    fileName = f"{safeName.lower()}sts.fext"
    currPath = os.path.join(sts.encryptDir, fileName)
    tempPath = os.path.join(sts.encryptDir, f"{prefix}{fileName}")
    try:
        if os.path.exists(currPath):
            os.rename(currPath, tempPath)
        yield
    finally:
        if os.path.exists(tempPath):
            if os.path.exists(currPath):
                os.remove(currPath)
            time.sleep(0.1)
            os.rename(tempPath, currPath)
            time.sleep(0.1)


def get_api_enpoint_dir(connector, *args, **kwargs):
    avAppsPath = unalias_path(sts.available_appsPaths)
    if os.path.isfile(avAppsPath):
        with open(avAppsPath, "r") as apps:
            available_apps = json.load(apps)
    else:
        appPath = os.getcwd()
        available_apps = {os.path.basename(appPath): [None, appPath]}
        connector = os.path.basename(appPath)
    app = available_apps.get(connector)
    if not app:
        raise Exception(f"no app found in available_appssts.fext named {connector}")
    else:
        return (sts.api_endpoints_path(unalias_path(app[1]), connector), unalias_path(app[1]))


# helper functions for unittest setup and teardown
def mk_test_file(tempDataDir, fileName, testDataStr=None, *args, **kwargs):
    """
    test files to be encrypted are created on the fly inside a temp directory
    """
    testFilePath = os.path.join(tempDataDir, fileName)
    testDataStr = sts.cryptonizeDataStr if testDataStr is None else testDataStr
    if testFilePath.endswith(".yml"):
        if not os.path.isfile(testFilePath):
            with open(testFilePath, "w") as f:
                f.write(yaml.dump(sts.testDataDict))
    elif testFilePath.endswith(".json"):
        if not os.path.isfile(testFilePath):
            with open(testFilePath, "w+") as f:
                json.dump(json.dumps(testDataStr, ensure_ascii=False), f)
    return testFilePath


# some test helper functions
def rm_test_dir(tempDir, *args, **kwargs):
    try:
        shutil.rmtree(tempDir, ignore_errors=False, onerror=None)
        # pass
    except Exception as e:
        print(f"UnitTest, tearDownClass, e: {e}")


def mk_test_dir(tempDirName, *args, **kwargs):
    """
    test files to be encrypted are created on the fly inside a temp directory
    """
    tempDataDir = os.path.join(sts.testDataDir, tempDirName)
    if not os.path.isdir(tempDataDir):
        os.makedirs(tempDataDir)
    time.sleep(0.1)
    return tempDataDir


def copy_test_data(tempDirName, testFileName, *args, targetName=None, **kwargs):
    print(testFileName)
    target = os.path.join(tempDirName, testFileName if targetName is None else targetName)
    shutil.copyfile(os.path.join(sts.testDataDir, testFileName), target)
    return target


def load_yml(testFilePath, *args, **kwargs):
    with open(testFilePath, "r") as f:
        return yaml.safe_load(f)


def load_str(testFilePath, *args, **kwargs):
    with open(testFilePath, "r") as f:
        return f.read()


def test_setup(*outer_args, **outer_kwargs):
    """
    A decorator for setting up a test environment with a temporary file, a specific
    working/execution directory and temporay passwords for encryption/decryption.
    This decorator uses two context managers:
        temp_test_file and temp_chdir. temp_test_file creates a
    temporary file for the test, and temp_chdir temporarily changes the
    current working directory.
    Args:
        *outer_args: Arguments for the temp_test_file context manager.
                     The first argument is expected to be the path for temp_chdir.
        **outer_kwargs: Keyword arguments for the temp_test_file context manager.
    Returns:
        The decorated test function.
    """

    def decorator(test_func):
        # The actual decorator that wraps the test function
        @functools.wraps(test_func)
        def wrapper(self, *inner_args, **inner_kwargs):
            # Wrapper function that sets up the test environment and executes the test
            # Use temp_test_file to create a temporary file
            with temp_test_file(test_func.__name__, *outer_args) as tempDataPath:
                # Use temp_chdir to change the current working directory
                with temp_chdir(outer_args[1]):
                    # use temporary testing passwords for encryption
                    # NOTE: this was formally included when calling unittest.main() on the
                    # test module. This did not always work however. So it was moved here.
                    with temp_password():
                        # Execute the test function with the path to the temporary files.
                        return test_func(self, tempDataPath, *inner_args, **inner_kwargs)

        return wrapper

    return decorator


@contextmanager
def temp_test_file(tempDirName: str, testDataFileName: str, *args) -> None:
    """
    Creates a temp dir named like test_func_name_to_be_tested and copies test data to it
    returns the full path to the copied file. The tempDir is removed when context is left.
    Example:
    Use this to create an isolated test data source named like the test function.
    The test file can then be read, changed, destroyed.
    testDataFileName, tempDirName = 'safe_one.json', 'test__prep_api_params'
    results in:
        1. created tempDir like sts.testDataDir/tempDirName
            tempDir = sts.testDataDir/test__prep_api_params/
        2. copies sts.testDataDir/safe_one.json to tempDir/safe_one.json
            tempPath = sts.testDataDir/test__prep_api_params/safe_one.json
    use like Example:
    with helpers.temp_test_file('test__prep_api_params', 'safe_one.json') as tempPath:
        run_any_test_using(tempPath)
    """
    sourcePath = os.path.join(sts.testDataDir, testDataFileName)
    assert os.path.isfile(sourcePath), f"file {sourcePath} not found"
    try:
        tempDir = os.path.join(sts.testDataDir, tempDirName)
        tempPath = os.path.join(tempDir, testDataFileName)
        if not os.path.isdir(tempDir):
            os.makedirs(tempDir)
        shutil.copyfile(sourcePath, tempPath)
        yield tempPath
    finally:
        if os.path.exists(tempDir):
            shutil.rmtree(tempDir, ignore_errors=False, onerror=None)


@contextmanager
def temp_password(*args, pw: str = None, **kwargs) -> None:
    try:
        os.environ["DATASAFEKEY"] = sts.testKeyOuter
        os.environ["DATAKEY"] = sts.testKeyInner
        yield
    finally:
        os.environ["DATASAFEKEY"] = sts.testKeyOuter
        os.environ["DATAKEY"] = sts.testKeyInner
