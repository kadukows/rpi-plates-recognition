from sqlalchemy.orm import Query

def get_whitelists_for_user_query(user) -> Query:
    from ..models import Whitelist

    return (Whitelist.query
        .filter(Whitelist.user == user))


def get_modules_for_user_query(user) -> Query:
    from ..models import Module, User

    return (Module.query.
        filter(Module.user == user))


def get_plates_for_whitelist_query(whitelist) -> Query:
    from ..models import Plate

    return Plate.query.filter(Plate.whitelist_id == whitelist.id)


def get_access_attempts_for_module_user_query(module, user) -> Query:
    from ..models import Module, User, AccessAttempt

    return (AccessAttempt.query
        .filter(AccessAttempt.module_id == module.id)
        .filter(AccessAttempt.user_id == user.id))


def get_access_attempts_for_user_query(user) -> Query:
    from ..models import AccessAttempt

    return (AccessAttempt.query
        .filter(AccessAttempt.user_id == user.id))
