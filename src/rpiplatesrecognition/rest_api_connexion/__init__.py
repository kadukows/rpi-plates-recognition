from connexion import RestyResolver
from .configurable_flask_app import ConfigurableFlaskApp

def init_connexion_app(connexion_app: ConfigurableFlaskApp):
    connexion_app.add_api('swagger.yml')
