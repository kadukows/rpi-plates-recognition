import numpy as np
import cv2 as cv


import os  # do usuniecia

img_size = (700, 550)


def preprocessing_image(img: np.ndarray):
    gauss_kernel = (3, 3)
    gauss_sigma = 7

    img = cv.medianBlur(img, 5)
    img = cv.equalizeHist(img)
    img = cv.GaussianBlur(img, (gauss_kernel), gauss_sigma)

    return img

def edge_detection(img: np.ndarray):
    threshold_down = 50
    morph_kernel_size = (50,12)

    rectKernel = cv.getStructuringElement(cv.MORPH_RECT, morph_kernel_size)
    img = cv.morphologyEx(img, cv.MORPH_TOPHAT, rectKernel)
    thresh,img = cv.threshold(img,threshold_down,255,cv.THRESH_TOZERO)

    return img

def draw_x_projection(proj_x,img):
    max_x = np.max(proj_x)
    width_proj = 500

    result = np.zeros((proj_x.shape[0], width_proj))
    for row in range(img.shape[0]):
        cv.line(result, (0, row), (int(proj_x[row] * width_proj / max_x), row), (255, 255, 255), 1)

    cv.imshow("X Projection", result)
    cv.waitKey()

def draw_y_projection(proj_y,img):
    height_proj = 500
    max_y = np.max(proj_y)

    result_y = np.zeros((height_proj, proj_y.shape[0]))
    for col in range(img.shape[1]):
        cv.line(result_y, (col, int(height_proj)), (col, int(height_proj - proj_y[col] * height_proj / max_y)),
                (255, 255, 255), 1)

    cv.imshow("Y Projection", result_y)
    cv.waitKey()

def find_up_and_down_bound(img):
    mean_size_x = 15
    possible_bounds = 3
    min_size_y = 50
    max_height = 100
    height_percent = 0.7

    lp_y_bounds = [] # (dolna granica, górna granica) ...

    proj_x = np.sum(img, 1)
    copy_x = proj_x.copy()
    proj_x[0:mean_size_x] = 0
    proj_x[len(proj_x) - mean_size_x:len(proj_x)] = 0

    for i in range(mean_size_x, len(proj_x) - mean_size_x):
        proj_x[i] = np.mean(copy_x[i - mean_size_x:i + mean_size_x])

    projection_x_edit = proj_x.copy()
    mean_proj = np.mean(proj_x)

    for i in range(0, possible_bounds):
        index = np.unravel_index(projection_x_edit.argmax(), projection_x_edit.shape)[0]

        up_bound = index + int(min_size_y / 2)  # default up bound

        for j in range(index + int(min_size_y / 2), index + int(max_height / 2)):
            if j >= img_size[1]:
                break

            if projection_x_edit[j] < height_percent * projection_x_edit[index]:
                up_bound = j
                break

        down_bound = index - int(min_size_y / 2)
        for j in range(index - int(min_size_y / 2), index - int(max_height / 2), -1):
            if j <= 0:
                break

            if projection_x_edit[j] < height_percent * projection_x_edit[index]:
                down_bound = j
                break

        projection_x_edit[down_bound: up_bound] = mean_proj
        lp_y_bounds.append((down_bound, up_bound))

    return lp_y_bounds

def get_bound_using_edge_projection(img: np.ndarray):
    mean_size_y = 65
    width_percent=0.45
    max_width = 600

    min_size_x = 120

    lp_y_bounds = find_up_and_down_bound(img)
    lp_x_bounds = []  # (lewa granica, prawa granica) ...

    proj_y = []
    for i in range(0, len(lp_y_bounds)):
        proj_y = np.sum(img[lp_y_bounds[i][0]: lp_y_bounds[i][1]][:], 0)
        mean_proj = np.mean(proj_y)
        projection_y_edit = proj_y.copy()
        projection_y_edit[0:mean_size_y] = 0
        projection_y_edit[len(projection_y_edit) - mean_size_y:len(projection_y_edit)] = 0

        for j in range(mean_size_y, len(projection_y_edit) - mean_size_y):
            projection_y_edit[j] = np.mean(proj_y[j - mean_size_y:j + mean_size_y])


        index = np.unravel_index(projection_y_edit.argmax(), projection_y_edit.shape)[0]

        right_bound = index + int(min_size_x/2)
        for k in range(index + int(min_size_x/2), index + int(max_width / 2)):
            if k >= img_size[0]:
                break

            if projection_y_edit[k] < width_percent * projection_y_edit[index]:
                right_bound = k
                break

        left_bound = index - int(min_size_x/2)
        for k in range(index - int(min_size_x/2), index - int(max_width / 2), -1):
            if k <= 0:
                break

            if projection_y_edit[k] < width_percent * projection_y_edit[index] :
                left_bound = k
                break

        projection_y_edit[left_bound: right_bound] = 0
        lp_x_bounds.append((left_bound, right_bound))


    return lp_x_bounds,lp_y_bounds


def chose_number_plate(proposed_areas,img):

    lp_x_bounds = proposed_areas[0]
    lp_y_bounds = proposed_areas[1]

    best_fit = [(0,0),(0,1),(0,2)]

    return best_fit


def edge_projection_algorithm(img: np.ndarray):
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img = cv.resize(img, img_size)
    img_copy = img.copy()

    img = preprocessing_image(img)
    img = edge_detection(img)
    proposed_areas = get_bound_using_edge_projection(img)

    lp_x_bounds = proposed_areas[0]
    lp_y_bounds = proposed_areas[1]

    best_fit = chose_number_plate(proposed_areas,img_copy)
    possible_plate = []

    for i in range(0,2):
        best = best_fit[i]
        cv.rectangle(img, (lp_x_bounds[best[0]][0], lp_y_bounds[best[1]][0]), (lp_x_bounds[best[0]][1], lp_y_bounds[best[1]][1]), (120, 120, 120))
        cv.imshow("test2", img)
        left = lp_x_bounds[best[0]][0]
        right = lp_x_bounds[best[0]][1]

        down = lp_y_bounds[best[1]][0]
        up = lp_y_bounds[best[1]][1]

        pic = img_copy[down:up,left:right]
        possible_plate.append(pic)
        cv.imshow("tablica",pic)
        cv.waitKey()

    return  possible_plate