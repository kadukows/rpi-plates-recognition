import base64
import click, os
from flask import current_app, Flask
from flask.app import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import shutil
import gzip


db = SQLAlchemy()

def init_db():
    from rpiplatesrecognition.models import AccessAttempt

    db.drop_all()
    db.create_all()
    try:
        shutil.rmtree(os.path.join(current_app.instance_path, AccessAttempt.STATIC_ROOT_DIR))
    except OSError:
        pass
    try:
        os.mkdir(os.path.join(current_app.instance_path, AccessAttempt.STATIC_ROOT_DIR))
    except FileExistsError:
        pass
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

    from ..models import User, Module, Whitelist, Plate, AccessAttempt, DEFAULT_EXTRACTION_PARAMS

    init_db()

    user = User(username='user1', password_hash=generate_password_hash('user1'))
    module = Module(unique_id='unique_id_1', extraction_params=DEFAULT_EXTRACTION_PARAMS)
    user.modules.append(module)

    admin = User(username='admin1', password_hash=generate_password_hash('admin1'), role='Admin')

    db.session.add(user)
    db.session.add(admin)
    db.session.add(module)

    for idx in range(2, 6):
        new_module = Module(unique_id=f'unique_id_{idx}')
        db.session.add(new_module)

    whitelist = Whitelist(name='example whitelist name')
    user.whitelists.append(whitelist)

    for plate_text in ['WA6642E', 'WI027HJ', 'ERA75TM', 'ERA81TL']:
        whitelist.plates.append(Plate(text=plate_text))

    with db.session.no_autoflush:
        for _ in range(5):
            with open(os.path.join(current_app.static_folder, 'debug.jpg'), 'rb') as file:
                encoded_image = base64.encodebytes(file.read())
            access_attempt = AccessAttempt(module, encoded_image)
            db.session.add(access_attempt)

    db.session.commit()

    click.echo('Initialized db with default values')

def init_app(app: Flask):
    db.init_app(app)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_db_debug_command)
    app.cli.add_command(init_db_backup_command)

    # workaround for quick development (ie quick app resets)
    with app.app_context():
        db.create_all()
        from ..models import Module
        Module.query.update({Module.is_active: False})
        db.session.commit()

    # this check for integrity of 'instance/photos' folder with dataabse state
    @app.before_first_request
    def access_attempts_integrity_check():
            from ..models import AccessAttempt
            access_attempts = AccessAttempt.query.all()
            assert all(access_attempt.photos_exist() for access_attempt in access_attempts), \
                "There are access attempts without photos existing, please reinit db with 'flask init-db' or 'flask init-db-debug'"


@click.command('init-db-backup')
@click.argument('directory',default='src/instance/photos')
@with_appcontext
def init_db_backup_command(directory ):
    """Command for creating backup of database and processed images"""
    shutil.make_archive('photo_backup', 'tar',directory)