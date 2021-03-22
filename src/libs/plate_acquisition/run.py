import numpy as np
import cv2 as cv



import os # do usuniecia

def preprocessing_image(img:np.ndarray):
    gauss_kernel = (3,3)
    gauss_sigma = 3
    img_size = (700,550)

    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img = cv.resize(img,img_size)
    img= cv.medianBlur(img, 3)
    img = cv.equalizeHist(img)    
    img = cv.GaussianBlur(img,(gauss_kernel),gauss_sigma)

    return img

def edge_detection(img:np.ndarray):
    low_bound = 170
    high_bound = 230
    #img = cv.Canny(img,low_bound,high_bound)
    rectKernel = cv.getStructuringElement(cv.MORPH_RECT,(15,8))
    img = cv.morphologyEx(img,cv.MORPH_TOPHAT,rectKernel)
    #kernel = np.ones((7,7),np.uint8)
    #img = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel,iterations=1)

    return img

def draw_projection(proj_x,proj_y,img):
    max_x = np.max(proj_x)
    max_y = np.max(proj_y)
    width_proj = 500
    height_proj = 500
    
    result = np.zeros((proj_x.shape[0],width_proj))
    for row in range(img.shape[0]):
        cv.line(result, (0,row), (int(proj_x[row]*width_proj/max_x),row), (255,255,255), 1)
    
    result_y = np.zeros((height_proj,proj_y.shape[0]))
    for col in range(img.shape[1]):
        cv.line(result_y, (col,height_proj), (col,height_proj-int(proj_y[col]*height_proj/max_y)), (255,255,255), 1)
    
    
    cv.imshow("projection",result)
    cv.imshow("projection y",result_y)




def edge_projection_with_window_function(img:np.ndarray):
    average_size=30
    
    proj_x = np.sum(img,1)
    proj_y = np.sum(img,0)
    copy_x = proj_x.copy()
    copy_y = proj_y.copy()    
    proj_x[0:average_size]=0
    proj_y[0:average_size]=0
    proj_x[len(proj_x)-average_size:len(proj_x)]=0
    proj_y[len(proj_y)-average_size:len(proj_y)]=0
    for i in range(average_size,len(proj_x)-average_size):
        proj_x[i] = np.mean(copy_x[i-average_size:i+average_size])
    
    for i in range(average_size,len(proj_y)-average_size):
        proj_y[i] = np.mean(copy_y[i-average_size:i+average_size])

    draw_projection(proj_x,proj_y,img)
    
    proj_x_copy =  proj_x.copy()
    index1=np.unravel_index(proj_x_copy.argmax(), proj_x_copy.shape)
    proj_x_copy[index1[0]-30:index1[0]+30]=0
    index2=np.unravel_index(proj_x_copy.argmax(), proj_x_copy.shape)
    print(index1,index2)

    cv.rectangle(img,(0,index1[0]-50),(600,index1[0]+50),(120,120,120))
    
    return img

def chose_one_number_plate(proposed_areas):
    return proposed_areas



def edge_projection_algorithm(img:np.ndarray):
    img = preprocessing_image(img)

    img = edge_detection(img)
    
    proposed_areas = edge_projection_with_window_function(img)
    cv.imshow("test2",img)
    img = chose_one_number_plate(proposed_areas)
    
    cv.waitKey()
    return img

def photo_to_plate(img:np.ndarray):
    img = edge_projection_algorithm(img)    
    return "LUB8890H"


def main():
    
    #img = cv.imread("images/PKR50972.png")
    #img = cv.imread("images/WA3230C.png")
    img = cv.imread("images/LUB8890H.png")
    photo_to_plate(img)
    

    
    directory = os.fsencode("images")
    
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        img = cv.imread("images/"+filename)
        photo_to_plate(img)
    
    
    


if __name__ == "__main__":
    main()

