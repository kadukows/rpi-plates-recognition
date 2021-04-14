import numpy as np

from .edge_projection_algorithm import edge_projection_algorithm
from .signs_extraction import find_segments

# this function convert image to recognized number plates string ( can be more than one )
def photo_to_plate(img: np.ndarray):


    # possible areas where plate can be recognized
    possible_plates = edge_projection_algorithm(img)


    segments = find_segments(possible_plates)

    # segments need to be 2D list

    # recognized_strings = recognize_plate(segments) # Tomek
    recognized_strings = ["abc12345","cba54321"]

    return recognized_strings
