import cv2
from pytesseract import image_to_string
img = cv2.imread('tablice/0.png')
plate = image_to_string(img, lang='eng',config='--psm 6')
print('License plate: ', plate)
