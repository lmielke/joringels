# encryption_handler.py

import os, time, yaml
import colorama as color

color.init()
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

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


# touch "decrypted_test_hint.yml" "TestJoringels: pyCallTestString"

tokenizers = {"&": "<and>", "@": "<at>"}
chunksize = 64 * 1024


class Handler:
    """handels encryption and decryption of param files
    call like:

    from joringels.src.encryption_handler import Handler as decryptor

    # h will provide:
    #                'h.decrypted':bool   - flag which confirms decryption
    #                'h.decryptPath':str  - path to decrypted file

    with decryptor(encryptPath, key) as h:
        if not h.decrypted: return False
        with open(h.decryptPath, 'r') as f:
            secrets = yaml.safe_load(f.read())
    """

    def __init__(
        self,
        *args,
        key=None,
        keyV=None,
        action=None,
        retain=False,
        write=False,
        verbose=0,
        **kwargs,
    ):
        self.verbose = verbose
        self.key, self.keyV = key, keyV
        self.action = action
        self.encryptPath, self.decryptPath = self._mk_secrets_paths(*args, **kwargs)
        self.retain, self.write = retain, write
        self._get_file_data(*args, **kwargs)

    def __enter__(self, *args, **kwargs):
        """
        decrypts file and saves it to self.decryptPath
        """
        self.cryptonize(*args, **kwargs)
        if self.write:
            self.write_decrypted(*args, **kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        """
        restore state
        """
        self.cleanup(*args, **kwargs)

    def cleanup(self, *args, **kwargs):
        """
        writes encrypted file and removes decrypted file on exit
        """
        # encrypted file is only removed if specifically asked for
        if self.action == "rm":
            self.remove_encrypted(*args, **kwargs)
            self.remove_decrypted(*args, **kwargs)
        else:
            self.write_encrypted(*args, **kwargs)
        # decrypted file is only preserved if specifically asked for
        if not self.retain:
            self.remove_decrypted(*args, **kwargs)

    def _mk_secrets_paths(self, filePath, *args, **kwargs) -> str:
        self.fileName, _, self.ext = os.path.basename(filePath).partition(".")
        if self.ext == sts.eext[1:]:
            encryptPath = filePath
            decryptPath = filePath.replace(sts.eext, sts.fext)
        elif self.ext == sts.fext[1:]:
            encryptPath = filePath.replace(sts.fext, sts.eext)
            decryptPath = filePath
        else:
            raise ValueError(f"wrong file extension: {self.ext}")
        return encryptPath, decryptPath

    def _get_file_data(self, _, secrets=None, *args, **kwargs):
        """
        reads file and returns data
        """
        self.data = {}
        if secrets is not None:
            try:
                self.isEncrypted = not bool(secrets.keys())
                self.data["encrypted"] = None
                self.data["decrypted"] = secrets
            except:
                self.isEncrypted = False
                self.data["decrypted"] = None
                self.data["encrypted"] = secrets
        elif os.path.isfile(self.encryptPath):
            self.data["decrypted"] = None
            with open(self.encryptPath, "r") as f:
                self.data["encrypted"] = f.read()
                self.isEncrypted = True
        elif os.path.isfile(self.decryptPath):
            self.data["encrypted"] = None
            with open(self.decryptPath, "r") as f:
                self.data["decrypted"] = yaml.safe_load(f.read())
                self.isEncrypted = False
                self.decryptedExists = True
        else:
            raise FileNotFoundError(f"file not found: {self.encryptPath}")

    def cryptonize(self, *args, key=None, keyV=None, **kwargs):
        """
        decrypts or encrypts file
        """
        # keys can not be provided as **kwargs if whith decryptor is used, hence __init__
        kwargs["key"] = key if key is not None else self.key
        kwargs["keyV"] = keyV if keyV is not None else self.keyV
        # assert self.key is not None, f"no key provided for {self.encryptPath}"
        assert self.data["decrypted"] or self.data["encrypted"], f"no data {self.encryptPath}"
        # encrypted file takes precedence, if it exists, existing decrypted file is ignored
        if self.data["decrypted"] is None:
            self.data["decrypted"] = dict_decrypt(self.data["encrypted"], **kwargs)
        # decrypted file is only checked and handled if not encrypted exists
        elif self.data["encrypted"] is None:
            self.data["encrypted"] = dict_encrypt(self.data["decrypted"], **kwargs)

    def change_key(self, newKey, newKeyV, *args, **kwargs):
        self.data["encrypted"] = dict_encrypt(self.data["decrypted"], newKey, newKeyV)

    def write_encrypted(self, *args, **kwargs):
        """
        writes encrypted file
        """
        with open(self.encryptPath, "w") as f:
            f.write(self.data["encrypted"])

    def write_decrypted(self, *args, **kwargs):
        """
        writes decrypted file
        """
        with open(self.decryptPath, "w") as f:
            f.write(yaml.dump(self.data["decrypted"]))

    def remove_decrypted(self, *args, **kwargs):
        """
        removes decrypted file
        """
        if not self.retain:
            if os.path.isfile(self.decryptPath):
                os.remove(self.decryptPath)

    def remove_encrypted(self, *args, **kwargs):
        """
        removes encrypted file
        """
        if os.path.isfile(self.encryptPath):
            os.remove(self.encryptPath)
