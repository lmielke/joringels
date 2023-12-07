from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
import base64
import os, json, hashlib

# uses https://www.pycryptodome.org version 3.9.9


def base64Encoding(input):
    dataBase64 = base64.b64encode(input)
    dataBase64P = dataBase64.decode("UTF-8")
    return dataBase64P


def base64Decoding(input):
    return base64.decodebytes(input.encode("ascii"))


def generateSalt32Byte():
    return get_random_bytes(32)


# encrypts and decrypts values and keys of a dictionary (entire dict)
def dict_encrypt(decrypted: dict, key: str = None, keyV: str = None) -> str:
    key = key if key is not None else os.environ.get("DATASAFEKEY")
    keyV = keyV if keyV is not None else os.environ.get("DATAKEY")
    # print(f"dict_encrypt: {key = }, {keyV = }")
    if type(decrypted) is not dict:
        return None
    return dict_keys_encrypt(dict_values_encrypt(decrypted, key=keyV), key=key)


def dict_decrypt(encrypted: str, key: str = None, keyV: str = None) -> dict:
    key = key if key is not None else os.environ.get("DATASAFEKEY")
    keyV = keyV if keyV is not None else os.environ.get("DATAKEY")
    # print(f"dict_decrypt: {key = }, {keyV = }")
    if type(encrypted) is not str:
        return None
    return dict_values_decrypt(dict_keys_decrypt(encrypted, key=key), key=keyV)


# encrypts and decrypts the values of a dictionary but leaves the key in plane text
def dict_values_encrypt(encrypted: dict, key: str = None) -> dict:
    key = key if key is not None else os.environ.get("DATAKEY")
    if type(encrypted) is not dict:
        return None
    return {k: text_encrypt(json.dumps(vs), key) for k, vs in encrypted.items()}


def dict_values_decrypt(decrypted: dict, key: str = None) -> dict:
    key = key if key is not None else os.environ.get("DATAKEY")
    if type(decrypted) is not dict:
        return None
    return {k: json.loads(str(text_decrypt(vs, key))) for k, vs in decrypted.items()}


# encrypts and decrypts a stringified dictionary (NOTE: values might still be encrypted)
def dict_keys_encrypt(decrypted: dict, key: str = None) -> str:
    key = key if key is not None else os.environ.get("DATASAFEKEY")
    if type(decrypted) is not dict:
        return None
    jsonStr = json.dumps(decrypted, ensure_ascii=False)
    decrypted.update({"checkSum": mk_checksum(jsonStr)})
    return text_encrypt(json.dumps(decrypted, ensure_ascii=False), key)


def dict_keys_decrypt(encrypted: str, key: str = None) -> dict:
    key = key if key is not None else os.environ.get("DATASAFEKEY")
    if type(encrypted) is not str:
        return None
    decrypted = json.loads(text_decrypt(encrypted, key))
    checkSum = decrypted["checkSum"]
    decrypted = {k: vs for k, vs in decrypted.items() if k != "checkSum"}
    if mk_checksum(json.dumps(decrypted, ensure_ascii=False)) != checkSum:
        return None
    else:
        return {int(k) if k.isnumeric() else k: vs for k, vs in decrypted.items()}


def text_encrypt(plaintext, key: str):
    salt = generateSalt32Byte()
    PBKDF2_ITERATIONS = 15000
    encryptionKey = PBKDF2(
        get_password(key), salt, 32, count=PBKDF2_ITERATIONS, hmac_hash_module=SHA256
    )
    cipher = AES.new(encryptionKey, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(str(plaintext).encode("ascii"), AES.block_size))
    ivBase64 = base64Encoding(cipher.iv)
    saltBase64 = base64Encoding(salt)
    ciphertextBase64 = base64Encoding(ciphertext)
    return saltBase64 + ":" + ivBase64 + ":" + ciphertextBase64


def text_decrypt(ciphertextBase64, key: str):
    data = ciphertextBase64.split(":")
    salt = base64Decoding(data[0])
    iv = base64Decoding(data[1])
    ciphertext = base64Decoding(data[2])
    PBKDF2_ITERATIONS = 15000
    decryptionKey = PBKDF2(
        get_password(key), salt, 32, count=PBKDF2_ITERATIONS, hmac_hash_module=SHA256
    )
    cipher = AES.new(decryptionKey, AES.MODE_CBC, iv)
    decryptedtext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    decryptedtextP = decryptedtext.decode("UTF-8")
    if decryptedtextP.isnumeric():
        decryptedtextP = int(decryptedtextP)
    return decryptedtextP


def get_password(key) -> str:
    if key is None:
        key = os.environ.get("DATAKEY")
    return key.encode("ascii")


def mk_checksum(jsonStr, *ags, **kwargs):
    return hashlib.md5(jsonStr.encode("utf-8")).hexdigest()


def main(params, key):
    # entcryption starts here
    encrypted = {
        k: text_encrypt(json.dumps(vs, ensure_ascii=False), key) for k, vs in params.items()
    }
    # decryption starts here
    decrypted = {}
    for k, ciphertextBase64 in encrypted.items():
        decryptedtext = text_decrypt(ciphertextBase64, key)
        decrypted[k] = json.loads(decryptedtext)
