import numpy as np
from pytesseract import image_to_string

from .edge_projection_algorithm import edge_projection_algorithm
from .signs_extraction import find_segments, combine_to_one
from .edge_projection_second import edge_projection_algorithm_v2
from .config_file import *


def global_edge_projection(img: np.ndarray, parameters: ExtractionConfigParameters):
    if parameters.algorithm_choice == 1:
        result = edge_projection_algorithm(img, parameters)
    elif parameters.algorithm_choice == 2:
        result = edge_projection_algorithm_v2(img, parameters)
    else:
        raise ValueError()

    return result

# this function convert image to recognized number plates string ( can be more than one )
def photo_to_plate(img: np.ndarray,parameters: ExtractionConfigParameters = ExtractionConfigParameters()):

    # possible areas where plate can be recognized
    if parameters.algorithm_choice == 1:
        possible_plates = edge_projection_algorithm(img, parameters)
    elif parameters.algorithm_choice == 2:
        possible_plates = edge_projection_algorithm_v2(img, parameters)
    else:
        raise ValueError()

    segments = find_segments(possible_plates,parameters)
    segment = combine_to_one(segments)
    recognized_strings = image_to_string(segment,lang='eng',config='--psm 6')

    return recognized_strings
