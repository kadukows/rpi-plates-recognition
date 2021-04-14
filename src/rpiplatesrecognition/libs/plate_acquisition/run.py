import numpy as np
import cv2 as cv
from .edge_projection_algorithm import *
from .signs_extraction import *


import os  # do usuniecia


# this function convert image to recognized number plates string ( can be more than one )
def photo_to_plate(img:np.ndarray):

    # possible areas where plate can be recognized
    possible_plates = edge_projection_algorithm(img)


    segments = find_segments(possible_plates)

    # segments need to be 2D list

    # recognized_strings = recognize_plate(segments) # Tomek
    recognized_strings = ["abc12345","cba54321"]

    return recognized_strings

def main():

    directory = os.fsencode("images")

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        img = cv.imread("images/"+filename)
        photo_to_plate(img)


if __name__ == "__main__":
    main()
