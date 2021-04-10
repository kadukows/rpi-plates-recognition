import numpy as np
import cv2 as cv



def adaptive_threshhold(img:np.ndarray):
    #img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret,img=cv.threshold(img,100,255,cv.THRESH_BINARY)
    #ret,img=cv.threshold(img,65,255,cv.THRESH_BINARY)
    #img=cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,11,2)
    #img= cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,11,2)
    img=cv.bitwise_not(img)
    return img


def  cca(img:np.ndarray):
    connectivity=4
    out=cv.connectedComponentsWithStats(img, connectivity, cv.CV_32S)
    stats=out[2]
    signs=[]

    for i in range(0,out[0]):
        if stats[i][3]>(0.4*len(img)) and (stats[i][3]/stats[i][2])>1.20:
            x=stats[i][0]
            y=stats[i][1]
            img2=img[y:y+stats[i][3],x:x+stats[i][2]]
            signs.append((x,y,img2))               
    
    signs.sort(key=lambda x:x[0])
    j=0
    while(j<len(signs)-1):
        if (signs[j][1]-10>signs[j+1][1] or signs[j][1]+10<signs[j+1][1]):
            del signs[j+1]
        else:
            j+=1

    only_signs=[]
    for i in signs:
        only_signs.append(i[2])

    return only_signs




def find_segments(possible_plates):

    found_signs=[]


    for img in possible_plates:
        img=adaptive_threshhold(img)
        signs=cca(img)
        if len(signs)>=4 and len(signs)<=8:
            found_signs=signs #There is one license plate assumed
            break
    for i in found_signs:
        cv.imshow("test2",i)
        cv.waitKey()

    return found_signs
