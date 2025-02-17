import os

def test_file_gen():
    with open("gigabyte.bin", 'wb') as f:
        for _ in range(1024):
            f.write(os.urandom(1024 * 1024))