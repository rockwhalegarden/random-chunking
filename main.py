import mmap
import shutil
import time

from chunk_processors.pixel import PixelChunkProcessor
from ipfs import download_file

def test_encryption():
    encryption_chunk_processor = PixelChunkProcessor([1, 3, 7, 1024 * 1024 * 1024 - 1], True)

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

    decryption_chunk_processor = PixelChunkProcessor(False)

    with open("downloads/gigabyte.bin", "rb") as f:
        mm = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)  # Maps entire file
        
        while chunk := mm.read(1024 * 1024):  # Read 1MB chunks
            decryption_chunk_processor.process_chunk(chunk, len(chunk) < 1024 * 1024)

        mm.close()
    
    decryption_chunk_processor.write_buffer.close()

# from aes import test_decryption

start = time.time()

test_encryption()
# test_decryption(["QmUY9QqnqAaPz8nuzKrbdcGBUfsyYsr9Nh4sp6LVWfDoU9", 
                #  "QmeXopKZ5jC3RVdEPLyqRfJbhwZQT5MrBqyz1utC4Ha4gq",
                #  "Qmchw5yYcqzQokVaRy2NhcqgcA6PE6eSKyMipbMS9Dmtgd",
                #  "QmTAekLZTC6LUDLhbzrZeudCyM3zUsqwvobAcpaR4VX7F1",
                #  "QmeV5THz57Kcv44PE6GGDewdyj41JNSfNdw4rWFNSzw1X3",
                #  "QmeV5THz57Kcv44PE6GGDewdyj41JNSfNdw4rWFNSzw1X3",
                #  "QmSbYUdTr6zws3VxcrhdKa9YC1RkVTSvxeewJwBx7TFuMF",
                #  "QmUC4qeKAukzRvyFViptYVEcbHKQdeHwwLEwDLrknPNMhj",
                #  "Qmf5ijsidNmZTzUfuE6ZunLSMGHdHLHQkr1rBTyW5aw76E",
                #  "QmUcETfM9g1biQVzY18AsY4PM4GZyp1s9fm9fafbS9fLDg",
                #  "QmQt6uUq5kom9ARvXKb8wLrDpudmvJPypYXvgTynM7jqR2"])

print(f"{time.time() - start}s elapsed")