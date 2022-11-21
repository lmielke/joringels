# encryption_handler.py

import os, time, yaml
import colorama as color

color.init()
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

import joringels.src.settings as sts

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

    def __init__(self, encryptPath, *args, key, retain=False, verbose=0, **kwargs):
        self.verbose = verbose
        self.decryptedExists = None
        self.encryptPath, self.decryptPath = self.mk_paths(encryptPath, *args, **kwargs)
        self.key = key
        self.retain = retain

    def __enter__(self, *args, **kwargs):
        """
        decrypts file and saves it to self.decryptPath
        """
        self.file_decrypt(*args, **kwargs)
        self.data_cleanup(self.decryptPath, "dec")
        return self

    def __exit__(self, *args, **kwargs):
        """
        removes decrypted file on exit
        """
        self.data_cleanup(self.decryptPath, "enc")
        encryptSuccess = None
        if self.decryptedExists:
            encryptSuccess = self.file_encrypt(*args, **kwargs)
        self.exit_cleanup(encryptSuccess, *args, **kwargs)

    def exit_cleanup(self, encryptSuccess, *args, **kwargs):
        if encryptSuccess == False or not self.retain:
            if os.path.isfile(self.encryptPath):
                os.remove(self.encryptPath)
        if os.path.isfile(self.decryptPath):
            os.remove(self.decryptPath)

    def mk_paths(self, secretPath: str, *args, **kwargs) -> tuple[str]:
        """
        takes a valid secretPath and creates the missing counter secretPath
        if encryptPath is given it creates the decryptPath
        if decryptPath is given it creates the encryptPath

        """
        secretsDir, secretsFileName = os.path.split(secretPath)
        if secretsFileName.startswith(sts.decPrefix):
            decFileName = secretsFileName
            secretsFileName = secretsFileName.replace(sts.decPrefix, "")
        decFileName = f"{sts.decPrefix}{secretsFileName}"
        decryptPath = os.path.join(secretsDir, decFileName)
        encryptPath = os.path.join(secretsDir, secretsFileName)
        if (not os.path.isfile(decryptPath)) and (not os.path.isfile(encryptPath)):
            msg = f"\njoringels.encryption_handler, secretPath not found: {secretPath}\n"
            print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
            raise FileNotFoundError
        elif os.path.isfile(decryptPath):
            self.decryptedExists = True
        else:
            self.decryptedExists = False
        return encryptPath, decryptPath

    def file_encrypt(self, *args, **kwargs):
        """
        ###Takes a file and encrypts its content.
        saves the encrpyted text to self.encryptPath
        """
        try:
            IV = Random.new().read(16)
            sha = SHA256.new(self.key.encode("utf-8")).digest()
            enc = AES.new(sha, AES.MODE_CBC, IV)
            with open(self.decryptPath, "rb") as inFile:
                with open(self.encryptPath, "wb") as outFile:
                    outFile.write(IV)
                    while chunk := inFile.read(chunksize):
                        if len(chunk) % 16:
                            chunk += b" " * (16 - (len(chunk) % 16))
                        outFile.write(enc.encrypt(chunk))
            return True
        except Exception as e:
            msg = f"encryption_handler.file_encrypt, Encryption failed ! : {e}"
            print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
            print(f"filePath: {self.encryptPath}")
            return False

    def file_decrypt(self, *args, **kwargs) -> bool:
        if self.decryptedExists:
            return None
        """
            reads a encrypted file from self.encryptPath and decrypts its content,
            saves extracted readable text to self.decryptPath file
        """
        try:
            with open(self.encryptPath, "rb") as inFile:
                IV = inFile.read(16)
                sha = SHA256.new(self.key.encode("utf-8")).digest()
                dec = AES.new(sha, AES.MODE_CBC, IV)
                with open(self.decryptPath, "wb") as outFile:
                    while chunk := inFile.read(chunksize):
                        outFile.write(dec.decrypt(chunk))
                with open(self.decryptPath, "rb") as f:
                    if fileSize := len(f.read()) == 0:
                        raise Exception(f"decrypted fileSize: {fileSize}")
            return True
        except Exception as e:
            print(f"file_decrypt, Exception: {e}")
            return False

    def data_cleanup(self, filePath: str, data: str, *args, **kwargs) -> bool:
        """
        cleans text and tokenizes decrypted file text
        notAllowed values such as & are replaced
        isValid allowes to confirm, that decryption result is readable
        """
        try:
            isValid, validator = True, "text_is_valid"
            with open(filePath, "r+") as f:
                text = f.read().strip()
                if data == "enc":
                    text = text.replace(validator, "")
                    text = text + validator
                elif data == "dec":
                    isValid = text.strip().endswith(validator)
                    text = text.replace(validator, "")
                for k, v in tokenizers.items():
                    text = text.replace(k, v) if data == "enc" else text.replace(v, k)
                f.seek(0)
                f.truncate()
                f.write(text.strip())
                time.sleep(0.1)
            # validate cleanup results
            if fileSize := str(len(text)).zfill(16) == 0:
                raise Exception(f"{data}: fileSize: {fileSize}")
            if not isValid:
                raise Exception(f"{data}: isValid: {isValid}")
            self.decryptedExists = True
        except UnicodeDecodeError as e:
            if self.verbose:
                print(f"Decryption Failed: {e}")
            self.decryptedExists = False
        except Exception as e:
            print(f"data_cleanup Error with data {data}: {e}")
            self.decryptedExists = False
