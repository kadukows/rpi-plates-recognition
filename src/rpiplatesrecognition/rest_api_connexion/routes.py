from enum import unique
from ..models import User, Module, Whitelist
from ..db import db

def get_modules(user: User):
    return {'modules': [module.unique_id for module in user.modules]}


def add_module(user: User, unique_id):
    module = Module.query.filter_by(unique_id = unique_id).first()

    if module is None:
        return '', 404

    if module.user is not None:
        return '', 409

    module.user = user
    db.session.commit()

    return '', 201


def remove_module(user: User, unique_id):
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
