"""
Parameters responsible for plates extraction
"""
class ExtractionConfigParameters():

    def __init__(self):
        self.algorithm_choice = 2  # 1 or 2

        self.img_size = (800, 600)
        self.max_areas = 2

        self.gauss_kernel = (3, 3)
        self.gauss_sigma = 7

        self.threshold_down = 50  # below this bound image pixels are set to 0
        self.morph_kernel_size = (50, 12)  # size of kernel has huge impact on result of morphology operation

        self.mean_size_x = 15  # to remove noises from projection - count mean of mean_size_x pixels
        self.possible_bounds = 3
        self.min_size_y = 30  # min height of possible area
        self.max_height = 100
        self.height_percent = 0.5  # this indicates where is the bound (bound is when height_percent * middle_pixel > pixel)

        self.mean_size_y = 65  # to remove noises from projection - count mean of mean_size_y pixels
        self.width_percent = 0.45  # this indicates where is the bound (bound is when width_percent * middle_pixel > pixel)
        self.max_width = 600
        self.min_size_x = 100

        ###########################################
        # second algorithm

        self.mean_size_x_v2 = 8  # to remove noises from projection - count mean of mean_size_x pixels
        self.min_size_y_v2 = 20  # min height of possible area
        self.height_percent_v2 = 0.45  # this indicates where is the bound (bound is when height_percent * middle_pixel > pixel)
        self.mean_size_y_v2 = 65  # to remove noises from projection - count mean of mean_size_y pixels
        self.width_percent_v2 = 0.50  # this indicates where is the bound (bound is when width_percent * middle_pixel > pixel)
        self.max_width_v2 = 600
        self.min_size_x_v2 = 150