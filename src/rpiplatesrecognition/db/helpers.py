def get_whitelists_for_user_query(user):
    from ..models import Whitelist, User

    return (Whitelist.query
        .join(User, Whitelist.user_id == User.id)
        .filter(User.id == user.id))


def get_modules_for_user_query(user):
    from ..models import Module, User

    return (Module.query
        .join(User, Module.user_id == User.id)
        .filter(User.id == user.id))
