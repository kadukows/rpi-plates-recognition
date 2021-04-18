import click, os
import cv2 as cv
from flask import Flask
from .libs.plate_acquisition import edge_projection_algorithm, find_segments, photo_to_plate

@click.command('possible_plates')
@click.argument('directory')
def possible_plates(directory):
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        img = cv.imread(os.path.join(directory, filename))

        photo_to_plate(img)



def init_app(app: Flask):
    app.cli.add_command(possible_plates)
