import numpy as np
import cv2 as cv

import os # do usuniecia

def photo_to_plate(img:np.ndarray):
    full_image=cv.resize(img,(1000,800))
    gray_img = cv.cvtColor(full_image, cv.COLOR_BGR2GRAY)
    #ret,thresh1 = cv.threshold(full_image,100,255,cv.THRESH_BINARY)
    
    cv
    cv.imshow("test",gray_img)
    cv.waitKey(0)









def main():
    
    img = cv.imread("images/PKR50972.png")
    photo_to_plate(img)
    

    
    directory = os.fsencode("images")
    
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        img = cv.imread("images/"+filename)
        photo_to_plate(img)

    
    


if __name__ == "__main__":
    main()

