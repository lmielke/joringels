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

def dict_values_encrypt(encrypted, password:str=os.environ.get("DATAKEY")):
    return ({k: text_encrypt(json.dumps(vs), password) for k, vs in encrypted.items()} )

def dict_values_decrypt(decrypted, password:str=os.environ.get("DATAKEY")):
    return ({k: json.loads(text_decrypt(vs, password)) for k, vs in decrypted.items()} )

def dict_encrypt(decrypted, password:str=os.environ.get("DATASAFEKEY")):
    """ 
        decrypts a dictionary which has been encrpyted with dict_encrypt
    """
    jsonStr = json.dumps(decrypted, ensure_ascii=False)
    decrypted.update({'encryption_dict_handler_checksum':
                            hashlib.md5(jsonStr.encode("utf-8")).hexdigest()})
    return text_encrypt(json.dumps(decrypted, ensure_ascii=False), password)

def dict_decrypt(encrypted:str, password:str=os.environ.get("DATASAFEKEY")) -> dict:
    out = text_decrypt(encrypted, password)
    decrypted = json.loads(out)
    checksum = decrypted['encryption_dict_handler_checksum']
    del decrypted['encryption_dict_handler_checksum']
    expected = hashlib.md5(json.dumps(decrypted, ensure_ascii=False).encode("utf-8")).hexdigest()
    if expected != checksum:
        decrypted = None
    decrypted = {int(k) if k.isnumeric() else k: vs for k, vs in decrypted.items()}
    return decrypted

def text_encrypt(plaintext, password:str=None):
    salt = generateSalt32Byte()
    PBKDF2_ITERATIONS = 15000
    encryptionKey = PBKDF2(
        get_password(password), 
        salt, 32, count=PBKDF2_ITERATIONS, hmac_hash_module=SHA256
    )
    cipher = AES.new(encryptionKey, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(str(plaintext).encode("ascii"), AES.block_size))
    ivBase64 = base64Encoding(cipher.iv)
    saltBase64 = base64Encoding(salt)
    ciphertextBase64 = base64Encoding(ciphertext)
    return saltBase64 + ":" + ivBase64 + ":" + ciphertextBase64


def text_decrypt(ciphertextBase64, password:str=None):
    data = ciphertextBase64.split(":")
    salt = base64Decoding(data[0])
    iv = base64Decoding(data[1])
    ciphertext = base64Decoding(data[2])
    PBKDF2_ITERATIONS = 15000
    decryptionKey = PBKDF2(
        get_password(password), 
        salt, 32, count=PBKDF2_ITERATIONS, hmac_hash_module=SHA256
    )
    cipher = AES.new(decryptionKey, AES.MODE_CBC, iv)
    decryptedtext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    decryptedtextP = decryptedtext.decode("UTF-8")
    if decryptedtextP.isnumeric(): decryptedtextP = int(decryptedtextP)
    return decryptedtextP

def get_password(password) -> str:
    if password is None:
        password = os.environ.get("DATAKEY")
    return password.encode("ascii")

def mk_checksum(*ags, **kwargs):
    pass

def main(params, password):
    # entcryption starts here
    print("SO AES CBC 256 encryption with PBKDF2 key derivation")
    encrypted = {k: text_encrypt(json.dumps(vs, ensure_ascii=False), password) for k, vs in params.items()}
    # decryption starts here
    decrypted = {}
    for k, ciphertextBase64 in encrypted.items():
        decryptedtext = text_decrypt(ciphertextBase64, password)
        decrypted[k] = json.loads(decryptedtext)


if __name__ == "__main__":
    with open(os.path.join(r"C:\Users\lars\.ssp", "_joringels.yml"), "r") as f:
        params = json.loads(f)
    main(params, "6789045129812345")
