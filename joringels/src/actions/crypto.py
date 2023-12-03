# crypto.py
import os, json, yaml
import colorama as color

color.init()
import joringels.src.settings as sts
import joringels.src.helpers as helpers
from joringels.src.encryption_dict_handler import (
    text_decrypt,
    text_encrypt,
    dict_encrypt,
    dict_decrypt,
    dict_values_decrypt,
    dict_values_encrypt,
)


def en_de_crypt(entry, *args, verbose, key: str = None, keyV: str = None, **kwargs):
    entry, entryType = get_type(entry)
    if entryType == dict:
        encrypted = dict_encrypt(entry, key=key, keyV=keyV)
        testResult = dict_decrypt(encrypted, key=key, keyV=keyV)
    elif entryType == str:
        encrypted = text_encrypt(entry, key=key)
        testResult = text_decrypt(encrypted, key=key)
    splitted = split_into_fstrings(encrypted)
    check = testResult == entry
    if check:
        msg = f"{color.Fore.GREEN}{testResult}{color.Fore.RESET}"
    else:
        msg = f"{color.Fore.RED}{testResult}{color.Fore.RESET}"
    if verbose >= 1:
        print(f"testFunc(out) == {msg} -> {check}")
    if verbose >= 1:
        print(f"{splitted}")
    return encrypted


def split_into_fstrings(text, chunk_size=70):
    # Split the text into chunks of `chunk_size` characters
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    # Format each chunk as an f-string and join them
    formatted_chunks = "\n\t\t".join(f'f"{chunk}"' for chunk in chunks)

    return f"out = (\n\t\t{formatted_chunks}\n\t)"


def get_type(entry):
    entryType = None
    try:
        jsonEntry = entry.strip('"').replace('"', "'")
        out = json.loads(f'"{jsonEntry}"')
        if type(out) == dict and out.keys():
            return out, dict
    except Exception as e:
        print("json: ", e)
    try:
        out = yaml.safe_load(entry)
        if type(out) == dict and out.keys():
            return out, dict
    except Exception as e:
        print("yaml", e)
    return entry, str


def main(*args, entryName, **kwargs) -> None:
    """
    imports source and connector from src and con argument
    then runs upload process using imported source an connector
    """
    assert entryName is not None, f"missing value for '-e entryName'"
    text = en_de_crypt(entryName, *args, **kwargs)
    return f"{text}"
