import mmap
import random
import shutil
import numpy as np
import time
import subprocess

def upload_file(path):
    subprocess.run(["ipfs", "add", path])
    subprocess.run(["ipfs", "pin", "add", path])
    print("")

def download_file(hash, path):
    subprocess.call(["ipfs", "get", hash, "-o", path])
    print("")

class BaseChunkProcessor:
    def __init__(self, is_encryption = True):
        random.seed(1)
        self.accumulated_bytes = 0  # number of bytes processed in the current patch
        self.random_chunk_size = random.randint(64, 128) * 1024  # current patch's bytes num
        self.patch_counter = 0  # counts how many patches are there in a single file
        self.accumulated_patch_counter = 0  # number of patches, without being reset
        self.is_encryption = is_encryption

        filename = f"encrypts/{self.accumulated_patch_counter}.rsb" if is_encryption else "decrypts/gigabyte.bin"
        self.write_buffer = open(filename, "wb")

    def process_chunk(self, data, eof = False):
        data_coordinates = 0
        while True:
            while self.accumulated_bytes < self.random_chunk_size:
                if len(data) - data_coordinates > self.random_chunk_size - self.accumulated_bytes:
                    to_write = data[data_coordinates : data_coordinates + self.random_chunk_size - self.accumulated_bytes]
                    self.write_buffer.write(bytes(255 - np.frombuffer(to_write, dtype=np.uint8)) if self.patch_counter % 2 == 0 else to_write)
                    data_coordinates += self.random_chunk_size - self.accumulated_bytes
                    self.accumulated_bytes += self.random_chunk_size - self.accumulated_bytes
                else:
                    to_write = data[data_coordinates:]
                    self.write_buffer.write(bytes(255 - np.frombuffer(to_write, dtype=np.uint8)) if self.patch_counter % 2 == 0 else to_write)
                    self.accumulated_bytes += len(data) - data_coordinates

                    if self.is_encryption and eof:
                        self.write_buffer.close()
                        upload_file(self.write_buffer.name)
                    return
            
            self.patch_counter += 1
            self.accumulated_patch_counter += 1
            self.accumulated_bytes = 0
            self.random_chunk_size = random.randint(64, 128) * 1024
            
            if self.is_encryption and self.patch_counter >= 1024:
                self.patch_counter = 0
                self.write_buffer.close()
                upload_file(self.write_buffer.name)
                self.write_buffer = open(f"encrypts/{self.accumulated_patch_counter}.rsb", "wb")

def test_encryption():
    encryption_chunk_processor = BaseChunkProcessor(True)

    with open("gigabyte.bin", "rb") as f:
        mm = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)  # Maps entire file
        
        while chunk := mm.read(1024 * 1024):  # Read 1MB chunks
            encryption_chunk_processor.process_chunk(chunk, len(chunk) < 1024 * 1024)

        mm.close()

def test_decryption(hash_list):
    for hash in hash_list:
        download_file(hash, f"downloads/{hash}.tmp")

    files = list(map(lambda x: f"downloads/{x}.tmp", hash_list))

    with open("downloads/gigabyte.bin", "wb") as outfile:
        for file in files:
            with open(file, "rb") as infile:
                shutil.copyfileobj(infile, outfile, length=1024 * 1024)

    decryption_chunk_processor = BaseChunkProcessor(False)

    with open("downloads/gigabyte.bin", "rb") as f:
        mm = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)  # Maps entire file
        
        while chunk := mm.read(1024 * 1024):  # Read 1MB chunks
            decryption_chunk_processor.process_chunk(chunk, len(chunk) < 1024 * 1024)

        mm.close()
    
    decryption_chunk_processor.write_buffer.close()

start = time.time()

# test_encryption()
test_decryption(["QmUY9QqnqAaPz8nuzKrbdcGBUfsyYsr9Nh4sp6LVWfDoU9", 
                 "QmeXopKZ5jC3RVdEPLyqRfJbhwZQT5MrBqyz1utC4Ha4gq",
                 "Qmchw5yYcqzQokVaRy2NhcqgcA6PE6eSKyMipbMS9Dmtgd",
                 "QmTAekLZTC6LUDLhbzrZeudCyM3zUsqwvobAcpaR4VX7F1",
                 "QmeV5THz57Kcv44PE6GGDewdyj41JNSfNdw4rWFNSzw1X3",
                 "QmeV5THz57Kcv44PE6GGDewdyj41JNSfNdw4rWFNSzw1X3",
                 "QmSbYUdTr6zws3VxcrhdKa9YC1RkVTSvxeewJwBx7TFuMF",
                 "QmUC4qeKAukzRvyFViptYVEcbHKQdeHwwLEwDLrknPNMhj",
                 "Qmf5ijsidNmZTzUfuE6ZunLSMGHdHLHQkr1rBTyW5aw76E",
                 "QmUcETfM9g1biQVzY18AsY4PM4GZyp1s9fm9fafbS9fLDg",
                 "QmQt6uUq5kom9ARvXKb8wLrDpudmvJPypYXvgTynM7jqR2"])

print(f"{time.time() - start}s elapsed")