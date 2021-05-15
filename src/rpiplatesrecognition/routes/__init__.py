from flask import Flask

def init_app(app: Flask):
    from . import access_attempts
    app.register_blueprint(access_attempts.bp)

    from . import admin_modules
    app.register_blueprint(admin_modules.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import index
    app.register_blueprint(index.bp)

    from . import modules
    app.register_blueprint(modules.bp)

    from . import rpi_connection
    app.register_blueprint(rpi_connection.bp)

    from . import user_profile
    app.register_blueprint(user_profile.bp)

    from . import whitelists
    app.register_blueprint(whitelists.bp)
