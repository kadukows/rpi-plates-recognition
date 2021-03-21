import os

from flask import Flask

def create_app(test_config=None):
    """This is default factory function for creating app object"""

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'rpiplatesrecognition.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        """This is a simple hello world route for testing ut framework"""

        return 'Hello, world!'

    from . import db
    db.init_app(app)

    from . import api
    app.register_blueprint(api.bp)

    return app
