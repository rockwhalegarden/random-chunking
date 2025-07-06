import subprocess
import time
import paho.mqtt.client as mqtt
import json
import os

broker = "127.0.0.1"
port = 1883
topic = "alcl/system/12D3KooWMjZDcEaFNDUqpEhSQj9N1P7QZFL1Mex71WoW2kmcF8K3/system_fetch_fragment"

client = mqtt.Client()
client.connect(broker, port, 60)


def upload_file(path):
    subprocess.run(["ipfs", "add", path])
    subprocess.run(["ipfs", "pin", "add", path])
    client.publish(topic, json.dumps({ "PATH": os.path.realpath(path) }))
    print("")

def download_file(hash, path):
    subprocess.call(["ipfs", "get", hash, "-o", path])
    print("")