"""
    gets secrets from a dataSafe
    NOTE: the dataSafe must contain the entry in its params.yml file
"""
import json, os, time, yaml
from contextlib import contextmanager

from joringels.src.actions import fetch


@contextmanager
def temp_secret(j, *args, secretsFilePath:str, entryName:str, **kwargs) -> None:
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
            if fType == '.json':
                json.dump(secrets, f)
            elif fType == '.yml':
                yaml.dump(secrets, f)
            else:
                raise Exception(f"Invalid file extension: {fType}, use [.json, .yml]")
        while not os.path.exists(secretsFilePath):
            continue
        yield
    except Exception as e:
        print(f"oamailer.secrets_loader Exception: {e}")
    finally:
        if os.path.exists(secretsFilePath):
            os.remove(secretsFilePath)
