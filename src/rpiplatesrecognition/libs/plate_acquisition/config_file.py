from typing import Tuple
from dataclasses import dataclass

"""
Parameters responsible for plates extraction
"""
@dataclass(frozen=True)
class ExtractionConfigParameters:

    algorithm_choice: int = 2  # 1 or 2

    img_size: Tuple[int, int] = (800, 600) #also passed to camera
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

    ###########################################
    # signs_extraction algorithm

    adaptive_threshhold_size: int = 11 #size of a pixel neighborhood that is used to calculate a threshold value
    adaptive_threshhold_C: int = 2 # constant subtracted from the mean
    connectivity: int = 4 #4 or 8 connectivity in cca algorithm
    min_len_per: float = 0.4 # the minimum percentage of the plate height that a character must occupy
    max_len_per: float = 1.01 # the maximum percentage of the height of the plate that a character can occupy
    max_diff_height: int = 7 # maximum number of pixels by which character height can be different
    min_wid_per: float = 0.025 # the minimum percentage of the plate weight that a character must occupy
    htw_ratio: float = 1.2 # the minimum ratio of the height to the width of the character
    threshold_morphology: int = 100 #below this bound image pixels are set to 0 after morphology operations
    min_number_of_ch: int = 4 # minimum number of characters found on plate
    max_number_of_ch: int = 9 # maximum number of characters found on plate

    ###########################################
    # camera

    camera_timeout_in_ms: int = 2000 #do not go below 1200
    camera_sharpness: int = 0 #-100 - 100
    camera_contrast: int = 0 #-100 - 100
    camera_brightness: int = 50 #-100 - 100
    camera_saturation: int = 0 #-100 - 100
    camera_quality: int = 100 #0 - 100

    ###########################################
    # gate controller

    gatecontroller_gpio_pin_number: int = 3
    gatecontroller_button_press_time: float = 0.35
    gatecontroller_gate_opening_time: float = 15
    gatecontroller_time_to_drive_in: float = 30


    def to_dict(self):
        from dataclasses import fields

        result = {}

        for field in fields(self):
            result[field.name] = _from_field(self, field)

        return result


def _from_field(var, field):
    import typing

    def type_to_str(type_):
        if type_ is int:
            return 'int'
        elif type_ is float:
            return 'float'
        elif type_ is typing.Tuple[int, int]:
            return 'Tuple[int]'
        else:
            raise NotImplementedError()

    return {
        'value': getattr(var, field.name),
        'type': type_to_str(field.type)
    }
