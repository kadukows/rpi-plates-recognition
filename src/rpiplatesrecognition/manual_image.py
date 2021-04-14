import click, os
import cv2 as cv
from flask import Flask
from .libs.plate_acquisition.plate_acquisition import

@click.command('possible_plates')
@click.argument('directory')
def possible_plates(directory):
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        img = cv.imread("images/"+filename)
        photo_to_plate(img)

def init_app(app: Flask):
    pass
