from rpi_camera import RaspberryPiCamera
import cv2 as cv2



def main():
    camera = RaspberryPiCamera()
    img = camera.take_photo()
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()