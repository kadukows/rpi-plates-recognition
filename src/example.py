import cv2
from camera import RaspberryPiCamera
from events import Event
from events import Observer


class MlTeam(Observer):
    def __init__(self):
        print("MlTeam waiting for camera event")
        Observer.__init__(self)

    def photo_ready(self, photo):
        print("Event received!")
        cv2.imshow('image',photo)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    
    team = MlTeam()
    team.observe('photo taken',  team.photo_ready)

    cam = RaspberryPiCamera()
    cam.take_photo()


if __name__ == '__main__':
    main()