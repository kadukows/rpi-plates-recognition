import cv2 as cv
import numpy as np

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