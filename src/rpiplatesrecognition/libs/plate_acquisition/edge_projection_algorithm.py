import numpy as np
import cv2 as cv
from .draw_projection import *
from .config_file import *
"""
from draw_projection import *
from config_file import *
"""

def preprocessing_image(img: np.ndarray,parameters):

    img = cv.medianBlur(img, 5)
    img = cv.equalizeHist(img)
    img = cv.GaussianBlur(img, parameters.gauss_kernel, parameters.gauss_sigma)
    return img

def morphology_operation(img: np.ndarray,parameters):

    rect_kernel = cv.getStructuringElement(cv.MORPH_RECT, parameters.morph_kernel_size)
    img = cv.morphologyEx(img, cv.MORPH_TOPHAT, rect_kernel)
    thresh, img = cv.threshold(img, parameters.threshold_down, 255, cv.THRESH_TOZERO)

    return img


def find_up_and_down_bound(img,parameters):

    lp_y_bounds = []  # (down bound, upper bound) ...

    proj_x = np.sum(img, 1)
    copy_x = proj_x.copy()
    proj_x[0:parameters.mean_size_x] = 0
    proj_x[len(proj_x) - parameters.mean_size_x:len(proj_x)] = 0

    for i in range(parameters.mean_size_x, len(proj_x) - parameters.mean_size_x):
        proj_x[i] = np.mean(copy_x[i - parameters.mean_size_x:i + parameters.mean_size_x])

    #draw_x_projection(proj_x,img)

    projection_x_edit = proj_x.copy()
    mean_proj = np.mean(proj_x)

    for i in range(0, parameters.possible_bounds):
        index = np.unravel_index(projection_x_edit.argmax(), projection_x_edit.shape)[0]

        up_bound = index + int(parameters.min_size_y / 2)  # default up bound

        for j in range(index + int(parameters.min_size_y / 2), index + int(parameters.max_height / 2)):
            if j >= parameters.img_size[1]:
                break

            if projection_x_edit[j] < parameters.height_percent * projection_x_edit[index]:
                up_bound = j
                break

        down_bound = index - int(parameters.min_size_y / 2)
        for j in range(index - int(parameters.min_size_y / 2), index - int(parameters.max_height / 2), -1):
            if j <= 0:
                break

            if projection_x_edit[j] < parameters.height_percent * projection_x_edit[index]:
                down_bound = j
                break

        projection_x_edit[down_bound: up_bound] = mean_proj
        lp_y_bounds.append((down_bound, up_bound))

    return lp_y_bounds


def get_bound_using_edge_projection(img: np.ndarray,parameters):

    lp_y_bounds = find_up_and_down_bound(img,parameters)
    lp_x_bounds = []  # (left bound, right bound) ...

    for i in range(0, len(lp_y_bounds)):
        proj_y = np.sum(img[lp_y_bounds[i][0]: lp_y_bounds[i][1]][:], 0)
        # mean_proj = np.mean(proj_y)
        projection_y_edit = proj_y.copy()
        projection_y_edit[0:parameters.mean_size_y] = 0
        projection_y_edit[len(projection_y_edit) - parameters.mean_size_y:len(projection_y_edit)] = 0

        for j in range(parameters.mean_size_y, len(projection_y_edit) - parameters.mean_size_y):
            projection_y_edit[j] = np.mean(proj_y[j - parameters.mean_size_y:j + parameters.mean_size_y])

        index = np.unravel_index(projection_y_edit.argmax(), projection_y_edit.shape)[0]

        right_bound = index + int(parameters.min_size_x/2)
        for k in range(index + int(parameters.min_size_x/2), index + int(parameters.max_width / 2)):
            if k >= parameters.img_size[0]:
                break

            if projection_y_edit[k] < parameters.width_percent * projection_y_edit[index]:
                right_bound = k
                break

        left_bound = index - int(parameters.min_size_x/2)
        for k in range(index - int(parameters.min_size_x/2), index - int(parameters.max_width / 2), -1):
            if k <= 0:
                break

            if projection_y_edit[k] < parameters.width_percent * projection_y_edit[index]:
                left_bound = k
                break

        projection_y_edit[left_bound: right_bound] = 0
        lp_x_bounds.append((left_bound, right_bound))

    return lp_x_bounds, lp_y_bounds


def chose_number_plate(proposed_areas, img,parameters):
    best_fit = []

    for i in range(0,parameters.max_areas):
        best_fit.append((0, i))

    return best_fit


def edge_projection_algorithm(img: np.ndarray, parameters:ExtractionConfigParameters):
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img = cv.resize(img, parameters.img_size)
    img_copy = img.copy()

    img = preprocessing_image(img, parameters)
    img = morphology_operation(img, parameters)
    proposed_areas = get_bound_using_edge_projection(img, parameters)

    lp_x_bounds = proposed_areas[0]
    lp_y_bounds = proposed_areas[1]

    best_fit = chose_number_plate(proposed_areas, img_copy, parameters)
    possible_plate = []

    """
    add possible ares to list and show them on image
    """

    for i in range(0, parameters.max_areas):
        best = best_fit[i]

        left = lp_x_bounds[best[0]][0]
        right = lp_x_bounds[best[0]][1]
        down = lp_y_bounds[best[1]][0]
        up = lp_y_bounds[best[1]][1]
        pic = img_copy[down:up, left:right]
        possible_plate.append(pic)


        cv.rectangle(img, (left, down), (right, up), (120, 120, 120), 2)
        #cv.imshow("test2", img)
        #cv.imshow("plate", pic)
        #cv.waitKey()



    return possible_plate
