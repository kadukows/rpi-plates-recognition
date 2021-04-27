import cv2 as cv
import numpy as np
#from .draw_projection import *

from draw_projection import *


def preprocessing_image_v2(img: np.ndarray, parameters):

    img = cv.medianBlur(img, 5)
    img = cv.equalizeHist(img)
    img = cv.GaussianBlur(img, parameters.gauss_kernel, parameters.gauss_sigma)
    return img

def morphology_operation_v2(img: np.ndarray, parameters):
    copy = img.copy()
    scale = 1
    delta = 0
    ddepth = cv.CV_16S

    img = cv.Sobel(img, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv.BORDER_DEFAULT)
    img = cv.convertScaleAbs(img)
    ret, img = cv.threshold(img, 0, 255, cv.THRESH_OTSU)

    return img


def find_up_and_down_bound_v2(img, parameters):

    lp_y_bounds = []  # (down bound, upper bound) ...

    proj_x = np.sum(img, 1)
    copy_x = proj_x.copy()
    proj_x[0:parameters.mean_size_x_v2] = 0
    proj_x[len(proj_x) - parameters.mean_size_x_v2:len(proj_x)] = 0

    for i in range(parameters.mean_size_x_v2, len(proj_x) - parameters.mean_size_x_v2):
        proj_x[i] = np.mean(copy_x[i - parameters.mean_size_x_v2:i + parameters.mean_size_x_v2])


    #draw_x_projection(proj_x,img) - to debug - find x projection

    projection_x_edit = proj_x.copy()
    mean_proj = np.mean(proj_x)

    for i in range(0, parameters.possible_bounds):
        index = np.unravel_index(projection_x_edit.argmax(), projection_x_edit.shape)[0]

        up_bound = index + int(parameters.min_size_y_v2 / 2)  # default up bound

        for j in range(index + int(parameters.min_size_y_v2 / 2), index + int(parameters.max_height / 2)):
            if j >= parameters.img_size[1]:
                break

            if projection_x_edit[j] < parameters.height_percent_v2 * projection_x_edit[index]:
                up_bound = j
                break

        down_bound = index - int(parameters.min_size_y_v2 / 2)
        for j in range(index - int(parameters.min_size_y_v2 / 2), index - int(parameters.max_height / 2), -1):
            if j <= 0:
                break

            if projection_x_edit[j] < parameters.height_percent_v2 * projection_x_edit[index]:
                down_bound = j
                break

        projection_x_edit[down_bound: up_bound] = mean_proj
        lp_y_bounds.append((down_bound, up_bound))

    return lp_y_bounds


def get_bound_using_edge_projection_v2(img: np.ndarray, parameters):

    lp_y_bounds = find_up_and_down_bound_v2(img, parameters)
    lp_x_bounds = []  # (left bound, right bound) ...

    for i in range(0, len(lp_y_bounds)):
        proj_y = np.sum(img[lp_y_bounds[i][0]: lp_y_bounds[i][1]][:], 0)
        # mean_proj = np.mean(proj_y)
        projection_y_edit = proj_y.copy()
        projection_y_edit[0:parameters.mean_size_y_v2] = 0
        projection_y_edit[len(projection_y_edit) - parameters.mean_size_y_v2:len(projection_y_edit)] = 0

        for j in range(parameters.mean_size_y_v2, len(projection_y_edit) - parameters.mean_size_y_v2):
            projection_y_edit[j] = np.mean(proj_y[j - parameters.mean_size_y_v2:j + parameters.mean_size_y_v2])

        index = np.unravel_index(projection_y_edit.argmax(), projection_y_edit.shape)[0]

        right_bound = index + int(parameters.min_size_x_v2/2)
        for k in range(index + int(parameters.min_size_x_v2/2), index + int(parameters.max_width_v2 / 2)):
            if k >= parameters.img_size[0]:
                break

            if projection_y_edit[k] < parameters.width_percent_v2 * projection_y_edit[index]:
                right_bound = k
                break

        left_bound = index - int(parameters.min_size_x_v2/2)
        for k in range(index - int(parameters.min_size_x_v2/2), index - int(parameters.max_width_v2 / 2), -1):
            if k <= 0:
                break

            if projection_y_edit[k] < parameters.width_percent_v2 * projection_y_edit[index]:
                left_bound = k
                break

        projection_y_edit[left_bound: right_bound] = 0
        lp_x_bounds.append((left_bound, right_bound))

    return lp_x_bounds, lp_y_bounds


def chose_number_plate_v2(proposed_areas, img, parameters):

    best_fit = []

    for i in range(0,parameters.max_areas):
        best_fit.append((0, i))

    return best_fit


def edge_projection_algorithm_v2(img: np.ndarray, parameters):
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img = cv.resize(img, parameters.img_size)
    img_copy = img.copy()

    img = preprocessing_image_v2(img, parameters)
    img = morphology_operation_v2(img, parameters)
    proposed_areas = get_bound_using_edge_projection_v2(img, parameters)

    lp_x_bounds = proposed_areas[0]
    lp_y_bounds = proposed_areas[1]

    best_fit = chose_number_plate_v2(proposed_areas, img_copy, parameters)
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
        cv.imshow("test2", img)

        cv.imshow("plate", pic)
        cv.waitKey()




    return possible_plate
