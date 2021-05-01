def get_whitelists_for_user_query(user):
    from ..models import Whitelist, User

    return (Whitelist.query
        .join(User, Whitelist.user_id == User.id)
        .filter(User.id == user.id))
