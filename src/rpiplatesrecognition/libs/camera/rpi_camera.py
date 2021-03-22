import numpy as np
import cv2 as cv2


class RaspberryPiCamera():
    def __init__(self):
        pass

    def take_photo(self) -> np.ndarray:
        print("Photo taken in class")

        #mock
        img = cv2.imread(
            '/mnt/c/Users/Lukasz-Lap/Desktop/vibingcatttt.jpg', 0)
        return img
        