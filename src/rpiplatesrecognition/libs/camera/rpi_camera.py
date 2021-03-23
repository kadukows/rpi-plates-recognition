import cv2 as cv2
import subprocess
import secrets
from typing import Tuple
import hashlib


class RaspberryPiCamera():
    def __init__(self):
        pass

    def take_photo(self):
        token = secrets.token_hex(32)

        full_filename = "/tmp/rpi-plates-recognition/" + \
                        str(int(hashlib.sha256(token.encode('utf-8')).hexdigest(), 16) %10**8) + \
                        ".jpg"
        cmd = "raspistill -o " + full_filename
        subprocess.call(cmd, shell=True)

        img = cv2.imread(full_filename)
        return token, img

    