import click
from flask import current_app, Flask
from flask.app import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized db')

@click.command('init-db-debug')
@with_appcontext
def init_db_debug_command():
    """Helper command for aiding development process, populates databse with default values"""

    from .models import User, Module, Whitelist, Plate

    init_db()

    user = User(username='user1', password_hash=generate_password_hash('user1'))
    module = Module(unique_id='unique_id_1')
    user.modules.append(module)

    admin = User(username='admin1', password_hash=generate_password_hash('admin1'), role='Admin')

    db.session.add(user)
    db.session.add(admin)

    whitelist = Whitelist(name='example whitelist name')
    user.whitelists.append(whitelist)

    for plate_text in ['WA6642E', 'WI027HJ', 'ERA75TM', 'ERA81TL']:
        whitelist.plates.append(Plate(text=plate_text))

    db.session.commit()

    click.echo('Initialized db with default values')

def init_app(app: Flask):
    db.init_app(app)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_db_debug_command)

    # workaround for quick development (ie quick app resets)
    with app.app_context():
        db.create_all()
        from .models import Module
        Module.query.update({Module.is_active: False})
        db.session.commit()
