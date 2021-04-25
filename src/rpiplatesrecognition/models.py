import base64, os, pickle
import enum
from typing import Tuple, List

import numpy as np
import cv2 as cv

import click
from flask import current_app
from flask.cli import with_appcontext
from flask_login import UserMixin
from sqlalchemy.orm import subqueryload
import sqlalchemy
from werkzeug.security import check_password_hash, generate_password_hash

from .db import db
from .helpers import files_in_dir
from .libs.plate_acquisition.config_file import ExtractionConfigParameters

DEFAULT_EXTRACTION_PARAMS = ExtractionConfigParameters()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(120), unique=True)
    # workaround, right now possible Values: 'Admin' and 'User'
    role = db.Column(db.String(12), index=False, unique=False, default='User')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


whitelist_to_module_assignment = db.Table("whitelist_to_module_assignment",
    db.Column('whitelist_id', db.Integer, db.ForeignKey('whitelists.id'), primary_key=True),
    db.Column('module_id', db.Integer, db.ForeignKey('modules.id'), primary_key=True)
)


class Module(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(32), index=True, unique=True)
    is_active = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('modules', lazy=True))

    whitelists = db.relationship('Whitelist', secondary=whitelist_to_module_assignment, lazy='subquery',
        backref=db.backref('modules', lazy=True))

    extraction_params = db.Column(db.PickleType, nullable=False, default=DEFAULT_EXTRACTION_PARAMS)

    def __repr__(self):
        return f'<Module {self.unique_id}>'


whitelist_assignment = db.Table('whitelist_assignments',
    db.Column('whitelist_id', db.Integer, db.ForeignKey('whitelists.id'), primary_key=True),
    db.Column('plate_id', db.Integer, db.ForeignKey('plates.id'), primary_key=True)
)

class Whitelist(db.Model):
    __tablename__ = 'whitelists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('whitelists', lazy=True))

    plates = db.relationship('Plate', secondary=whitelist_assignment, lazy='subquery',
        backref=db.backref('whitelists', lazy=True))


class Plate(db.Model):
    __tablename__ = 'plates'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(10), unique=True, index=True, nullable=False)


class AccessAttempt(db.Model):
    __tablename__ = 'access_attempts'

    def __init__(self, module: Module, extraction_params: ExtractionConfigParameters = None):
        self.module = module
        self.user = self.module.user
        self.extraction_params = extraction_params or module.extraction_params

    def init_files(self, encoded_image: bytes):
        from .libs.plate_acquisition import find_segments, global_edge_projection

        self.save_src_image(encoded_image)
        img = cv.imread(os.path.join(current_app.static_folder, self.get_src_image_static_filepath()))

        possible_plates = global_edge_projection(img, self.extraction_params)
        self.save_edge_projection(possible_plates)

        segments = find_segments(possible_plates)
        self.save_segments(segments)



    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), nullable=False, server_default=sqlalchemy.sql.func.now())

    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    module = db.relationship('Module', backref=db.backref('access_attempts', lazy=True))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('accessaccess_attempts', lazy=True))

    extraction_params = db.Column(db.PickleType, nullable=False, default=DEFAULT_EXTRACTION_PARAMS)


    STATIC_ROOT_DIR = 'photos'
    SRC_IMAGE_NAME = 'src.jpg'
    EDGE_PROJECTION_ALGO_DIR = 'edge_projection'
    SEGMENTS_ALGO_DIR = 'segments'



    def get_src_image_relative_directory(self):
        """ Gets images directory as seen in static folder, f.e.: 'photos/user1/unique_id_1/1' """

        assert (self.id is not None
            and self.module is not None
            and self.user is not None)

        user = self.user
        module = self.module

        return os.path.join(AccessAttempt.STATIC_ROOT_DIR, user.username, module.unique_id, str(self.id))

    def get_edge_proj_relative_directory(self):
        """ Gets images directory as seen in static folder, f.e.: 'photos/user1/unique_id_1/1/edge_projection' """

        src_img_rel_dir = self.get_src_image_relative_directory()
        return os.path.join(src_img_rel_dir, AccessAttempt.EDGE_PROJECTION_ALGO_DIR)

    def get_segments_relative_directory(self):
        """ Gets images directory as seen in static folder, f.e.: 'photos/user1/unique_id_1/1/segments' """

        src_img_rel_dir = self.get_src_image_relative_directory()
        return os.path.join(src_img_rel_dir, AccessAttempt.SEGMENTS_ALGO_DIR)



    def _try_create_dir(self, dir: str):
        try:
            os.makedirs(dir)
        except OSError:
            pass

    def save_src_image(self, base64_encoded_image: bytes):
        """ Saves source (original) image to root of relative_directory"""

        image_abs_directory = os.path.join(current_app.static_folder, self.get_src_image_relative_directory())
        self._try_create_dir(image_abs_directory)
        with open(os.path.join(image_abs_directory, AccessAttempt.SRC_IMAGE_NAME), 'wb') as file:
            file.write(base64.decodebytes(base64_encoded_image))

    def save_edge_projection(self, plates_regions: List[np.ndarray]):
        """ Saves all regions from edge_projection to ralative_directory/edge_projection """

        image_abs_directory = os.path.join(current_app.static_folder, self.get_edge_proj_relative_directory())
        self._try_create_dir(image_abs_directory)
        for idx, plate_region in enumerate(plates_regions):
            assert cv.imwrite(os.path.join(image_abs_directory, str(idx) + '.png'), plate_region)

    def save_segments(self, segments: List[np.ndarray]):
        """ Saves all segments from edge_projection to ralative_directory/segments """

        image_abs_directory = os.path.join(current_app.static_folder, self.get_segments_relative_directory())
        self._try_create_dir(image_abs_directory)
        for idx, segment in enumerate(segments):
            assert cv.imwrite(os.path.join(image_abs_directory, str(idx) + '.png'), segment)



    def get_src_image_static_filepath(self) -> str:
        """ Gets images filepath as seen in static folder, f.e.: 'photos/user1/unique_id_1/1/src.jpg' """

        return os.path.join(self.get_src_image_relative_directory(), AccessAttempt.SRC_IMAGE_NAME)

    def get_edge_proj_static_filepaths(self) -> List[str]:
        """ Gets images filepaths as seen in static folder, f.e.: '[photos/user1/unique_id_1/1/edge_projection/1.png, ...]' """

        edge_proj_dir = self.get_edge_proj_relative_directory()
        return [os.path.join(edge_proj_dir, filename) for filename in files_in_dir(os.path.join(current_app.static_folder, edge_proj_dir))]

    def get_segments_static_filepaths(self) -> List[str]:
        """ Gets images filepaths as seen in static folder, f.e.: '[photos/user1/unique_id_1/1/segments/1.png, ...]' """

        segments_dir = self.get_segments_relative_directory()
        return [os.path.join(segments_dir, filename) for filename in files_in_dir(os.path.join(current_app.static_folder, segments_dir))]
