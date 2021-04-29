import connexion
import flask
from connexion.apps.flask_app import FlaskJSONEncoder

class ConfigurableFlaskApp(connexion.FlaskApp):
    def __init__(self, import_name, **kwargs):
        self.flask_args = _get_flask_args(kwargs)
        connexion_args = _get_connexion_args(kwargs)
        super().__init__(import_name, **connexion_args)

    def create_app(self):
        app = flask.Flask(self.import_name, **self.flask_args)
        app.json_encoder = FlaskJSONEncoder
        return app

def _get_flask_args(kwargs):
    return {k.replace('flask_', ''): v for k, v in kwargs.items() if k.startswith('flask_')}

def _get_connexion_args(kwargs):
    return {k: v for k, v in kwargs.items() if not k.startswith('flask_')}
