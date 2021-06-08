import os
from enum import unique
from ..models import AccessAttempt, User, Module, Whitelist, Plate, Dirs
from ..db import db
from ..db.helpers import get_access_attempts_for_user_query, get_modules_for_user_query, get_whitelists_for_user_query

from flask import send_from_directory
from connexion import NoContent

def get_modules(user: User):
    return {'modules': [
        {
            'unique_id': module.unique_id,
            'whitelists': [whitelist.name for whitelist in module.whitelists]
        } for module in user.modules
    ]}


def bind_module(user: User, unique_id):
    module = Module.query.filter_by(unique_id = unique_id).first()

    if module is None:
        return NoContent, 404

    if module.user is not None:
        return NoContent, 409

    module.user = user
    db.session.commit()

    return NoContent, 201


def unbind_module(user: User, unique_id):
    module = Module.query.filter_by(unique_id = unique_id).first()

    if module is None:
        return NoContent, 404

    if module.user.id != user.id:
        return NoContent, 412

    module.user = None
    db.session.commit()

    return NoContent, 201


def create_whitelist(user: User, whitelist_name):
    whitelist = Whitelist.query.filter_by(name=whitelist_name).first()

    if whitelist is not None:
        return NoContent, 412

    whitelist = Whitelist(name=whitelist_name)
    whitelist.user = user
    db.session.add(whitelist)
    db.session.commit()

    return NoContent, 201


def get_whitelists(user: User):
    return {'whitelists': [whitelist.name for whitelist in user.whitelists]}


def get_plates_in_whitelist(user: User, whitelist_name):
    whitelist = (Whitelist.query
        .join(User, Whitelist.user_id == User.id)
        .filter(User.id == user.id)
        .filter(Whitelist.name == whitelist_name)).first()

    if whitelist is None:
        return NoContent, 404

    return {
        'whitelist_name': whitelist_name,
        'plates': [plate.text for plate in whitelist.plates]
    }


def add_plate_to_whitelist(user: User, whitelist_name: str, plate_text: str):
    plate_text = plate_text.upper()

    if Plate.is_valid_plate(plate_text) is None:
        return NoContent, 412

    whitelist = (Whitelist.query
        .join(User, Whitelist.user_id == User.id)
        .filter(User.id == user.id)
        .filter(Whitelist.name == whitelist_name)).first()

    if whitelist is None:
        return NoContent, 409

    possible_plate = (Plate.query
        .join(Whitelist, Plate.id == Whitelist.id)
        .filter(Whitelist.id == whitelist.id)
        .filter(Plate.text == plate_text)).first()

    if possible_plate is None:
        plate = Plate(text=plate_text)
        whitelist.plates.append(plate)
        db.session.commit()

    return NoContent, 201


def register(new_user):
    possible_user = User.query.filter_by(username=new_user['username']).first()

    if possible_user is not None:
        return 'Username already taken', 409

    if not User.does_password_comply_to_policy(new_user['password']):
        return 'Password does not comply to policy', 409

    user = User(username=new_user['username'], email=new_user['email'])
    user.set_password(new_user['password'])

    db.session.add(user)
    db.session.commit()

    return NoContent, 201


def get_access_attempts_for_module(user: User, unique_id: str):
    possible_module = get_modules_for_user_query(user).filter(Module.unique_id == unique_id).first()

    if possible_module is None:
        return NoContent, 403

    return {
        'access_attempts': [
            access_attempt.to_dict() for access_attempt in possible_module.access_attempts
        ]
    }


def get_photo_for_access_attempt(user: User, access_attempt_id: int):
    possible_access_attempt = get_access_attempts_for_user_query(user).filter(AccessAttempt.id == access_attempt_id).first()

    if possible_access_attempt is None:
        return NoContent, 403

    dirname, filename = os.path.split(possible_access_attempt.get_src_image_filepath(Dirs.Absolute))
    return send_from_directory(dirname, filename)


def bind_whitelist_to_module(user: User, whitelist_name: str, unique_id: str):
    module = get_modules_for_user_query(user).filter_by(unique_id=unique_id).first()
    if module is None:
        return NoContent, 412

    whitelist = get_whitelists_for_user_query(user).filter_by(name=whitelist_name).first()
    if whitelist is None:
        return NoContent, 409

    module.whitelists.append(whitelist)
    db.session.commit()
    return NoContent, 201


def unbind_whitelist_from_module(user: User, whitelist_name: str, unique_id: str):
    module = get_modules_for_user_query(user).filter_by(unique_id=unique_id).first()
    if module is None:
        return NoContent, 412

    whitelist = get_whitelists_for_user_query(user).filter_by(name=whitelist_name).first()
    if whitelist is None:
        return NoContent, 409

    try:
        module.whitelists.remove(whitelist)
    except:
        pass
    db.session.commit()
    return NoContent, 201
