import os, enum
from typing import Tuple
from flask import current_app, request
from sqlalchemy.orm import Query
from flask_wtf import FlaskForm

def files_in_dir(path: str):
    return (file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)))


def create_new_directory_for_photo(encoded_photo: bytes) -> str:
    from hashlib import sha1

    photo_path = os.path.join(current_app.instance_path, 'photos')
    hashed_photo = sha1(encoded_photo).hexdigest()

    created = False
    number = None
    # THIS NEEDS BETTER IMPLEMENTATION
    while not created:
        try:
            hashed_photo_result = hashed_photo + ('_' + str(number) if number is not None else '')
            os.mkdir(os.path.join(photo_path, hashed_photo_result))
            created = True
        except FileExistsError:
            number = number + 1 if number is not None else 1
            pass

    return hashed_photo_result

class Dirs(enum.Enum):
    Relative = 0
    Absolute = 1

    @classmethod
    def get_dir(dirs_class, access_attempt, dir_enum):
        if dir_enum == dirs_class.Relative:
            return access_attempt.get_relative_dir()
        else:
            return access_attempt.get_absolute_dir()


def process_bootstrap_table_request(query: Query, searchField, orderField) -> Tuple[int, int, Query]:
    totalNotFiltered = query.count()

    search = request.args.get('search', '', type=str)
    query = query.filter(searchField.like(f'%{search}%'))
    total = query.count()

    order = request.args.get('order', 'asc', type=str)
    if order == 'desc':
        query = query.order_by(orderField.desc())
    else:
        query = query.order_by(orderField.asc())

    offset = request.args.get('offset', 0, type=int)
    query = query.offset(offset)

    limit = request.args.get('limit', 10, type=int)
    query = query.limit(limit)

    return (total, totalNotFiltered, query)


class AjaxForm(FlaskForm):
    def generate_failed_response_dict(self):
        result = {'errors': {}}

        for field in self:
            if field.errors:
                result['errors'][field.name] = [error for error in field.errors]

        return result
