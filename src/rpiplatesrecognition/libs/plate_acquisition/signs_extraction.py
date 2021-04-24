import numpy as np
import cv2 as cv
from typing import List



def adaptive_threshhold(img:np.ndarray):
    #img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    #ret,img=cv.threshold(img,100,255,cv.THRESH_BINARY)
    #ret,img=cv.threshold(img,65,255,cv.THRESH_BINARY)
    img=cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,11,2)
    #img= cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,11,2)
    img=cv.bitwise_not(img)
    return img


def  cca(img:np.ndarray):
    connectivity=4
    out=cv.connectedComponentsWithStats(img, connectivity, cv.CV_32S)
    stats=out[2]
    signs=[]

    #Assumptions:
    #Character is at least 40% of the plate
    #Character is up to 90% of the plate
    #The ratio of the height to the width of the character is greater than 1.2

    for i in range(0,out[0]):
        if stats[i][3]>(0.4*len(img)) and (stats[i][3]/stats[i][2])>1.20 and stats[i][3]<(0.9*len(img)):
            x=stats[i][0]
            y=stats[i][1]
            img2=img[y:y+stats[i][3],x:x+stats[i][2]+1]
            signs.append((x,y,img2))

    signs.sort(key=lambda x:x[0])
    j=0
    while(j<len(signs)-1):
        if (signs[j][1]-10>signs[j+1][1] or signs[j][1]+10<signs[j+1][1] or len(signs[j+1][2])<len(signs[j][2])-10):
            del signs[j+1]
        else:
            j+=1

    only_signs=[]
    for i in signs:
        only_signs.append(i[2])

    return only_signs


def flood_fill(sign):
    sign_floodfill=sign.copy()
    h, w = sign.shape[:2]
    mask = np.zeros((h+2,w+2), np.uint8)

    cv.floodFill(sign_floodfill, mask, (0,0) , 255)

    sign_floodfill=cv.bitwise_not(sign_floodfill)

    floodfilled_sign=sign | sign_floodfill
    return floodfilled_sign


def sign_morphology(sign):
    sign=cv.resize(sign,(int(len(sign[0])*2),int(len(sign)*2)))
    kernel=np.ones((5,5),np.uint8)
    opened_sign=cv.morphologyEx(sign,cv.MORPH_OPEN,kernel)
    opened_sign=cv.morphologyEx(opened_sign,cv.MORPH_OPEN,kernel)
    closed_sign=cv.morphologyEx(opened_sign,cv.MORPH_CLOSE,kernel)
    #closed_sign=cv.morphologyEx(closed_sign,cv.MORPH_CLOSE,kernel)
    ret,result_sign=cv.threshold(closed_sign,100,255,cv.THRESH_BINARY)
    return result_sign


def find_segments(possible_plates) -> List[np.ndarray]:

    found_signs=[]


    for img in possible_plates:
        img=adaptive_threshhold(img)
        #cv.imshow("test2",img)
        #cv.waitKey()
        signs=cca(img)
        #cv.waitKey()
        if len(signs)>=4 and len(signs)<=9:
            found_signs=signs #There is one license plate assumed
            break
    for i in found_signs:
        i=sign_morphology(i)
        #cv.imshow("test2",i)
        #cv.waitKey()

    return found_signs
