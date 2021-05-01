from enum import unique
from ..models import User, Module, Whitelist, Plate
from ..db import db

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
        return '', 404

    if module.user is not None:
        return '', 409

    module.user = user
    db.session.commit()

    return '', 201


def unbind_module(user: User, unique_id):
    module = Module.query.filter_by(unique_id = unique_id).first()

    if module is None:
        return '', 404

    if module.user.id != user.id:
        return '', 412

    module.user = None
    db.session.commit()

    return '', 201


def create_whitelist(user: User, whitelist_name):
    whitelist = Whitelist.query.filter_by(name=whitelist_name).first()

    if whitelist is not None:
        return '', 412

    whitelist = Whitelist(name=whitelist_name)

    return '', 201


def get_whitelists(user: User):
    return {'whitelists': [whitelist.name for whitelist in user.whitelists]}


def get_plates_in_whitelist(user: User, whitelist_name):
    whitelist = (Whitelist.query
        .join(User, Whitelist.user_id == User.id)
        .filter(User.id == user.id)
        .filter(Whitelist.name == whitelist_name)).first()

    if whitelist is None:
        return '', 404

    return {
        'whitelist_name': whitelist_name,
        'plates': [plate.text for plate in whitelist.plates]
    }


def add_plate_to_whitelist(user: User, whitelist_name: str, plate_text: str):
    plate_text = plate_text.capitalize()

    if Plate.is_valid_plate(plate_text) is None:
        return '', 412

    whitelist = (Whitelist.query
        .join(User, Whitelist.user_id == User.id)
        .filter(User.id == user.id)
        .filter(Whitelist.name == whitelist_name)).first()

    if whitelist is None:
        return '', 409

    possible_plate = (Plate.query
        .join(Whitelist, Plate.id == Whitelist.id)
        .filter(Whitelist.id == whitelist.id)
        .filter(Plate.text == plate_text)).first()

    if possible_plate is None:
        plate = Plate(text=plate_text)
        whitelist.plates.append(plate)
        db.session.commit()

    return '', 201


def register(new_user):
    possible_user = User.query.filter_by(username=new_user['username']).first()

    if possible_user is not None:
        return 'Username already taken', 409

    if not User.does_password_comply_to_policy(new_user['password']):
        return 'Password does not comply to policy', 409

    user = User(username=new_user['username'])
    user.set_password(new_user['password'])

    db.session.add(user)
    db.session.commit()

    return '', 201
