from typing import Tuple
from dataclasses import dataclass

"""
Parameters responsible for plates extraction
"""
@dataclass
class ExtractionConfigParameters:

    algorithm_choice: int = 1  # 1 or 2

    img_size: Tuple[int, int] = (800, 600)
    max_areas: int = 2

    gauss_kernel: Tuple[int, int] = (3, 3)
    gauss_sigma: int = 7

    threshold_down: int = 50  # below this bound image pixels are set to 0
    morph_kernel_size: Tuple[int, int] = (50, 12)  # size of kernel has huge impact on result of morphology operation

    mean_size_x: int = 15  # to remove noises from projection - count mean of mean_size_x pixels
    possible_bounds: int = 3
    min_size_y: int = 30  # min height of possible area
    max_height: int = 100
    height_percent: float = 0.5  # this indicates where is the bound (bound is when height_percent * middle_pixel > pixel)

    mean_size_y: int = 65  # to remove noises from projection - count mean of mean_size_y pixels
    width_percent: float = 0.45  # this indicates where is the bound (bound is when width_percent * middle_pixel > pixel)
    max_width: int = 600
    min_size_x: int = 100

        ###########################################
        # second algorithm

    mean_size_x_v2: int = 8  # to remove noises from projection - count mean of mean_size_x pixels
    min_size_y_v2: int = 20  # min height of possible area
    height_percent_v2: float = 0.45  # this indicates where is the bound (bound is when height_percent * middle_pixel > pixel)
    mean_size_y_v2: int = 65  # to remove noises from projection - count mean of mean_size_y pixels
    width_percent_v2: float = 0.50  # this indicates where is the bound (bound is when width_percent * middle_pixel > pixel)
    max_width_v2: int = 600
    min_size_x_v2: int = 150