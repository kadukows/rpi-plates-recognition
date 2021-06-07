import base64, os, pickle, re, enum
import enum, json
from typing import Tuple, List

import numpy as np
import cv2 as cv

import click
from flask import current_app, Flask
from flask_login import UserMixin
from sqlalchemy.orm import subqueryload
import sqlalchemy
from werkzeug.security import check_password_hash, generate_password_hash
import keras, tensorflow
from keras.preprocessing import image
from .db import db
from .helpers import files_in_dir, create_new_directory_for_photo, Dirs
from .libs.plate_acquisition.config_file import ExtractionConfigParameters

DEFAULT_EXTRACTION_PARAMS = ExtractionConfigParameters()

class UserRoleEnum(enum.IntEnum):
    User = 1
    Admin = 2

class UserRole(db.Model):
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Enum(UserRoleEnum), unique=True, nullable=False)

    def __eq__(self, other: UserRoleEnum):
        if isinstance(other, UserRoleEnum):
            return self.value == other

        raise RuntimeError('UserRole::__eq__(): wrong type')

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True,nullable=False)
    user_role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'), nullable=False, default=UserRoleEnum.User)
    user_role = db.relationship('UserRole')


    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_user(self):
        return self.user_role == UserRoleEnum.User

    def is_admin(self):
        return self.user_role == UserRoleEnum.Admin

    @staticmethod
    def does_password_comply_to_policy(password) -> bool:
        # TO BE IMPLEMENTED
        return True


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


class Whitelist(db.Model):
    __tablename__ = 'whitelists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('whitelists', lazy=True))


class Plate(db.Model):
    __tablename__ = 'plates'

    def __init__(self, text, **kwargs):
        assert Plate.is_valid_plate(text)
        db.Model.__init__(self, text=text, **kwargs)

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(10), unique=False, index=True, nullable=False)

    whitelist_id = db.Column(db.Integer, db.ForeignKey('whitelists.id'), nullable=False)
    whitelist = db.relationship('Whitelist', backref=db.backref('plates', lazy=True, cascade="all, delete-orphan"))

    PLATE_RE = re.compile(r'[A-Z]{2,3}[A-Z0-9]{3,5}')

    @staticmethod
    def is_valid_plate(text):
        return Plate.PLATE_RE.match(text)


class AccessAttempt(db.Model):
    __tablename__ = 'access_attempts'

    def __init__(self,
            module: Module,
            encoded_image: bytes,
            extraction_params: ExtractionConfigParameters = None):
        self.module = module
        self.model = keras.models.load_model('character_recognition.h5')
        self.user = self.module.user
        extraction_params_ = extraction_params or module.extraction_params
        self.extraction_params = extraction_params_
        self.photos_dir = create_new_directory_for_photo(encoded_image)
        self.init_directories() # inits dirs for segments and edge porjection results
        self.characters = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, \
            '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'A': 10, 'B': 11, 'C': 12, \
            'D': 13, 'E': 14, 'F': 15, 'G': 16, 'H': 17, 'I': 18, \
            'J': 19, 'K': 20, 'L': 21, 'M': 22, 'N': 23, 'O': 24, \
            'P': 25, 'Q': 26, 'R': 27, 'S': 28, 'T': 29, 'U': 30, 'V': 31, \
            'W': 32, 'X': 33, 'Y': 34, 'Z': 35}

        from .libs.plate_acquisition import find_segments, global_edge_projection, combine_to_one
        from pytesseract import image_to_string

        # save original photo
        with open(self.get_src_image_filepath(Dirs.Absolute), 'wb') as file:
            file.write(base64.b64decode(encoded_image))

        img = cv.imread(self.get_src_image_filepath(Dirs.Absolute))
        assert img is not None

        # save plate regions
        plates_regions = global_edge_projection(img, extraction_params_)
        if plates_regions is None:
            self.plate_region_num = 0
            self.segments_num = 0
            self.recognized_plate = "Plate region empty"

        else:
            self.plate_region_num = len(plates_regions)
            for idx, plate_region in enumerate(plates_regions):
                assert cv.imwrite(
                    os.path.join(self.get_edge_proj_dirpath(Dirs.Absolute), str(idx) + '.png'),
                    plate_region)

            # save segments
            segments = find_segments(plates_regions, extraction_params_)
            if segments is None:
                self.segments_num = 0
                self.recognized_plate = "Segments empty"

            else:
                segments_one = combine_to_one(segments)
                self.segments_num = 1
                # quick hack for better table in html
                for idx, segment in enumerate([segments_one]):
                    assert cv.imwrite(
                        os.path.join(self.get_segments_dirpath(Dirs.Absolute), str(idx) + '.png'),
                        segment)
                if extraction_params_.sign_recognition_choice == 0:
                    self.recognized_plate = image_to_string(segments_one, lang='eng', config='--psm 6')
                else:
                    
                    plate = ''
                    for segment in segments:
                        segment=cv.resize(segment, (128, 128))
                        img_segment=np.empty([128,128,3])
                        for j in range(0, len(segment)):
                            for k in range(0, len(segment[0])):
                                img_segment[j][k]=[segment[j][k], segment[j][k], segment[j][k]]
                        img_tensor = np.expand_dims(img_segment, axis=0)
                        prediction = np.argmax(self.model.predict(img_tensor))
                        name = []
                        for char, number in self.characters.items():
                            if number == prediction:
                                name = char
                                break
                        plate += str(name)

                    #self.recognized_plate = plate + str(len(segments))
                    self.recognized_plate = plate
                possible_plate_groups = Plate.PLATE_RE.search(self.recognized_plate)
                if possible_plate_groups is not None:
                    self.processed_plate_string = possible_plate_groups.group(0)

                    query = sqlalchemy.text('''
                        SELECT plates.id
                        FROM plates
                            INNER JOIN whitelists ON plates.whitelist_id = whitelists.id
                            INNER JOIN whitelist_to_module_assignment ON whitelists.id = whitelist_to_module_assignment.whitelist_id
                        WHERE
                            whitelist_to_module_assignment.module_id = :module_id
                            AND plates.text = :plate_text
                    ''').bindparams(module_id=self.module.id, plate_text=self.processed_plate_string)

                    possible_plate_id = db.session.execute(query).fetchone()

                    if possible_plate_id is not None:
                        self.got_access = True





    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), nullable=False, server_default=sqlalchemy.sql.func.now())

    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    module = db.relationship('Module', backref=db.backref('access_attempts', lazy=True))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('access_attempts', lazy=True))

    plate_region_num = db.Column(db.Integer, nullable=False)
    segments_num = db.Column(db.Integer, nullable=False)
    recognized_plate = db.Column(db.String(30), nullable=False)
    processed_plate_string = db.Column(db.String(15), nullable=False, default='')
    got_access = db.Column(db.Boolean, nullable=False, default=False)
    extraction_params = db.Column(db.PickleType, nullable=False, default=DEFAULT_EXTRACTION_PARAMS)
    photos_dir = db.Column(db.String(120), nullable=False)


    STATIC_ROOT_DIR = 'photos'
    SRC_IMAGE_NAME = 'src.jpg'
    EDGE_PROJECTION_ALGO_DIR = 'edge_projection'
    SEGMENTS_ALGO_DIR = 'segments'


    def photos_exist(self) -> bool:
        return os.path.exists(self.get_absolute_dir())

    def get_absolute_dir(self):
        return os.path.join(current_app.instance_path, self.get_relative_dir())

    def get_relative_dir(self):
        return os.path.join(AccessAttempt.STATIC_ROOT_DIR, self.photos_dir)

    def get_src_image_filepath(self, dir_enum):
        return os.path.join(Dirs.get_dir(self, dir_enum), AccessAttempt.SRC_IMAGE_NAME)

    def get_edge_proj_dirpath(self, dir_enum):
        return os.path.join(Dirs.get_dir(self, dir_enum), AccessAttempt.EDGE_PROJECTION_ALGO_DIR)

    def get_segments_dirpath(self, dir_enum):
        return os.path.join(Dirs.get_dir(self, dir_enum), AccessAttempt.SEGMENTS_ALGO_DIR)

    def init_directories(self):
        os.mkdir(self.get_edge_proj_dirpath(Dirs.Absolute))
        os.mkdir(self.get_segments_dirpath(Dirs.Absolute))

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%d.%m.%y %H:%M:%S'),
            'plate': self.recognized_plate,
            'processed_plate_string': self.processed_plate_string,
            'got_access': self.got_access
        }