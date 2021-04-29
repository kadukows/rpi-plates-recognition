from rpiplatesrecognition.models import User


def verify_password(username, password, required_scopes=None):
    user = User.query.filter_by(username=username).first()
    user: User

    if user and user.check_password(password):
        return {'sub': user}

    return None
