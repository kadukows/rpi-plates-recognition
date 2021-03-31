import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

import os  # do usuniecia


def preprocessing_image(img: np.ndarray):
    gauss_kernel = (3, 3)
    gauss_sigma = 3
    img_size = (700, 550)

    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img = cv.resize(img, img_size)
    img = cv.medianBlur(img, 3)
    img = cv.equalizeHist(img)
    img = cv.GaussianBlur(img, (gauss_kernel), gauss_sigma)

    return img


def edge_detection(img: np.ndarray):

    rectKernel = cv.getStructuringElement(cv.MORPH_RECT, (15, 8))
    img = cv.morphologyEx(img, cv.MORPH_TOPHAT, rectKernel)

    return img


def draw_projection(proj_x, proj_y, img):
    max_x = np.max(proj_x)
    max_y = np.max(proj_y)
    width_proj = 500
    height_proj = 500

    result = np.zeros((proj_x.shape[0], width_proj))
    for row in range(img.shape[0]):
        cv.line(result, (0, row), (int(proj_x[row] * width_proj / max_x), row), (255, 255, 255), 1)

    result_y = np.zeros((height_proj, proj_y.shape[0]))
    for col in range(img.shape[1]):
        cv.line(result_y, (col, height_proj), (col, height_proj - int(proj_y[col] * height_proj / max_y)),
                (255, 255, 255), 1)


    cv.imshow("projection", result)
    cv.imshow("projection y", result_y)


def edge_projection_with_window_function(img: np.ndarray):
    mean_size_x = 15
    mean_size_y = 30
    height_percent = 0.7
    max_height = 80
    possible_bounds = 3
    possible_horizontal = 3
    lp_y_bounds = [] # (dolna granica, górna granica) ...
    lp_x_bounds = []  # (lewa granica, prawa granica) ...

    proj_x = np.sum(img, 1)
    copy_x = proj_x.copy()
    proj_x[0:mean_size_x] = 0
    proj_x[len(proj_x) - mean_size_x:len(proj_x)] = 0
    for i in range(mean_size_x, len(proj_x) - mean_size_x):
        proj_x[i] = np.mean(copy_x[i - mean_size_x:i + mean_size_x])


    proj_x_copy = proj_x.copy()
    for i in range(0,possible_bounds):
        index = np.unravel_index(proj_x_copy.argmax(), proj_x_copy.shape)[0]

        up_bound= index
        for j in range(index,index + int(max_height/2)):
            if proj_x_copy[j] < height_percent * proj_x_copy[index]:
                up_bound = j
                break

        down_bound= index
        for j in range(index - int(max_height/2),index):
            if proj_x_copy[j] < height_percent * proj_x_copy[index]:
                down_bound = j
                break

        proj_x_copy[index - 20: index + 20] = 0
        lp_y_bounds.append((down_bound,up_bound))

    # found x values

    proj_y = []
    columns = []
    for i in range(0, 3):
        proj_y = np.sum(img[lp_y_bounds[i][0]: lp_y_bounds[i][1]][:], 0)
        copy_y = proj_y
        copy_y[0:mean_size_y] = 0
        copy_y[len(copy_y) - mean_size_y:len(copy_y)] = 0

        for j in range(mean_size_y, len(copy_y) - mean_size_y):
            copy_y[j] = np.mean(proj_y[j - mean_size_y:j + mean_size_y])

        columns.append(np.unravel_index(proj_y.argmax(), proj_y.shape)[0])


    draw_projection(proj_x, proj_y, img)


    for i in range(0,3):
        cv.rectangle(img, (columns[i]-100, lp_y_bounds[i][0]), (columns[i]+100, lp_y_bounds[i][1]), (120, 120, 120))
        cv.imshow("test2", img)
        cv.waitKey()


    return img


def chose_one_number_plate(proposed_areas):
    return proposed_areas


def edge_projection_algorithm(img: np.ndarray):
    img = preprocessing_image(img)

    img = edge_detection(img)

    proposed_areas = edge_projection_with_window_function(img)

    img = chose_one_number_plate(proposed_areas)

    cv.waitKey()
    return img