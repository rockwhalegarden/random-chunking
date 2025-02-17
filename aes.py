import os
import subprocess
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import time

def upload_file(path):
    subprocess.call(["ipfs", "add", path])
    print("")

def download_file(hash, path):
    subprocess.call(["ipfs", "get", hash, "-o", path])
    print("")

def test_encryption(key):
    cipher = AES.new(key, AES.MODE_GCM)
    nonce = cipher.nonce

    with open("gigabyte.bin", 'rb') as f:
        raw_contents = f.read()

    ciphertext, tag = cipher.encrypt_and_digest(raw_contents)

    with open("encrypts/gigabyte_enc.bin", 'wb') as f:
        f.write(nonce)
        f.write(tag)
        f.write(ciphertext)
    
    upload_file("encrypts/gigabyte_enc.bin")


def test_decryption(hash, key):
    download_file(hash, "downloads/gigabyte_enc.bin")

    with open("downloads/gigabyte_enc.bin", 'rb') as f:
        nonce = f.read(16)
        tag = f.read(16)
        ciphertext = f.read()

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)

    with open("decrypts/gigabyte.bin", 'wb') as f:
        f.write(plaintext)

key = get_random_bytes(32)
print(f"Encryption Key: {key.hex()}")

start = time.time()

# test_encryption(key)
test_decryption("QmWKC2Zgmb2HB79wvmiz8WNvriYUephzFZgaKeDsNb76MG", bytes.fromhex("c3ec69a748af53ff208fd459220021d52afdbc666b7cb8015950e19d57d56549"))

print(f"{time.time() - start}s elapsed")
