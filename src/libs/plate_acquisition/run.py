import numpy as np
import cv2 as cv
from edge_projection_algorithm import *

import os  # do usuniecia


def photo_to_plate(img:np.ndarray):
    possible_plates = edge_projection_algorithm(img)

    return "LUB8890H"

def main():

    directory = os.fsencode("images")
    
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        img = cv.imread("images/"+filename)
        photo_to_plate(img)


if __name__ == "__main__":
    main()

