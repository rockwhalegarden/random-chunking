import subprocess


def upload_file(path):
    subprocess.run(["ipfs", "add", path])
    subprocess.run(["ipfs", "pin", "add", path])
    print("")

def download_file(hash, path):
    subprocess.call(["ipfs", "get", hash, "-o", path])
    print("")