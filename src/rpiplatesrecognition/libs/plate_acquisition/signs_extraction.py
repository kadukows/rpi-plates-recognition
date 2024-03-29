import numpy as np
import cv2 as cv
from typing import List

from .draw_projection import *
from .config_file import *

"""
from draw_projection import *
from config_file import *
"""


def adaptive_threshhold(img:np.ndarray, parameters):
    #img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    #ret,img=cv.threshold(img,100,255,cv.THRESH_BINARY)
    #ret,img=cv.threshold(img,65,255,cv.THRESH_BINARY)
    img=cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,parameters.adaptive_threshhold_size,parameters.adaptive_threshhold_C)
    #img= cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,11,2)
    img=cv.bitwise_not(img)
    return img


def  cca(img:np.ndarray,parameters):
    out=cv.connectedComponentsWithStats(img, parameters.connectivity, cv.CV_32S)
    stats=out[2]
    signs=[]

    #Assumptions:
    #Character is at least 40% of the plate
    #Character is up to 90% of the plate
    #The ratio of the height to the width of the character is greater than 1.2

    for i in range(0,out[0]):
        if stats[i][3]>(parameters.min_len_per*len(img)) and (stats[i][3]/stats[i][2])>parameters.htw_ratio and stats[i][3]<(parameters.max_len_per*len(img)) and stats[i][2]>(parameters.min_wid_per*len(img[0])):
            x=stats[i][0]
            y=stats[i][1]
            img2=img[y:y+stats[i][3],x:x+stats[i][2]+1]
            signs.append((x,y,img2))

    signs.sort(key=lambda x:x[0])
    j=0
    while(j<len(signs)-1):
        if (signs[j][1]-parameters.max_diff_height>signs[j+1][1] or signs[j][1]+parameters.max_diff_height<signs[j+1][1] or len(signs[j+1][2])<len(signs[j][2])-parameters.max_diff_height):
            del signs[j+1]
        else:
            j+=1

    only_signs=[]
    for i in signs:
        only_signs.append(i[2])

    return only_signs

def clear_characters(signs):
    connectivity=4
    for img in signs:
        out=cv.connectedComponentsWithStats(img, connectivity, cv.CV_32S)
        while(out[0]>2):
            stats=out[2]
            if (stats[1][4]>stats[2][4]):
                check=2
            else:
                check=1
            x=stats[check][0]
            y=stats[check][1]
            for i in range(x,x+stats[check][2]+1):
                for j in range(y,y+stats[check][3]+1):
                    img[j][i]=0
            out=cv.connectedComponentsWithStats(img, connectivity, cv.CV_32S)
    return signs


def flood_fill(sign):
    sign_floodfill=sign.copy()
    h, w = sign.shape[:2]
    mask = np.zeros((h+2,w+2), np.uint8)

    cv.floodFill(sign_floodfill, mask, (0,0) , 255)

    sign_floodfill=cv.bitwise_not(sign_floodfill)

    floodfilled_sign=sign | sign_floodfill
    return floodfilled_sign


def sign_morphology(sign, threshold_value):
    sign=cv.resize(sign,(int(len(sign[0])*2),int(len(sign)*2)))
    kernel=np.ones((5,5),np.uint8)
    opened_sign=cv.morphologyEx(sign,cv.MORPH_OPEN,kernel)
    opened_sign=cv.morphologyEx(opened_sign,cv.MORPH_OPEN,kernel)
    closed_sign=cv.morphologyEx(opened_sign,cv.MORPH_CLOSE,kernel)
    #closed_sign=cv.morphologyEx(closed_sign,cv.MORPH_CLOSE,kernel)
    ret,result_sign=cv.threshold(closed_sign,threshold_value,255,cv.THRESH_BINARY)
    return result_sign


def combine_to_one(img_list):
    if len(img_list) == 0:
        return
    img_list=[cv.bitwise_not(img) for img in img_list]
    h_max=max(img.shape[0] for img in img_list)
    img_list=[cv.resize(img,(int(img.shape[1]*h_max/img.shape[0]),h_max),interpolation=cv.INTER_CUBIC) for img in img_list]
    #img_list=[cv.copyMakeBorder(img,5,5,5,5,cv.BORDER_CONSTANT,value=255) for img in img_list]
    return cv.hconcat(img_list)


def find_segments(possible_plates,parameters:ExtractionConfigParameters) -> List[np.ndarray] :

    found_signs=[]


    for img in possible_plates:
        img=adaptive_threshhold(img,parameters)
        #cv.imshow("test",img)
        #cv.waitKey()
        signs=cca(img,parameters)
        #cv.waitKey()
        if len(signs)>=parameters.min_number_of_ch and len(signs)<=parameters.max_number_of_ch:
            found_signs=signs #There is one license plate assumed
            break
    for i in range (0,len(found_signs)):
        found_signs[i]=sign_morphology(found_signs[i],parameters.threshold_morphology)
        found_signs[i]=cv.copyMakeBorder(found_signs[i],5,5,5,5,cv.BORDER_CONSTANT,value=0)
        #cv.imshow("test2",i)
        #cv.waitKey()
    found_signs=clear_characters(found_signs)
    if len(found_signs)==0:
        return None
    return found_signs
