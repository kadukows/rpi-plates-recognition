import os, enum

from flask import current_app

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
    def get_dir(dirs_class, access_attempt, dir_enum) -> str:
        if dir_enum == dirs_class.Relative:
            return access_attempt.get_relative_dir()
        else:
            return access_attempt.get_absolute_dir()
