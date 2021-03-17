from .camera_interfaces import ICamera
import events
import numpy as np
import cv2 as cv2
from events import Event


class RaspberryPiCamera(ICamera):
    def __init__(self):
        pass

    def take_photo(self):
        print("Photo taken in class")
        img = cv2.imread(
            '/home/pi/plates_recognition/rpi-plates-recognition/src/static/photos/elmo.png', 0)

        Event("photo taken", img)
