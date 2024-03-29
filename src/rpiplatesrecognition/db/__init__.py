import base64
import click, os
from flask import current_app, Flask
from flask.app import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import shutil,gzip,time


db = SQLAlchemy()

def init_db():
    from rpiplatesrecognition.models import AccessAttempt, UserRole, UserRoleEnum

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

    role_user = UserRole(id=int(UserRoleEnum.User), value=UserRoleEnum.User)
    role_admin = UserRole(id=int(UserRoleEnum.Admin), value=UserRoleEnum.Admin)

    db.session.add(role_user)
    db.session.add(role_admin)

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

    from ..models import User, Module, Whitelist, Plate, AccessAttempt, DEFAULT_EXTRACTION_PARAMS, UserRoleEnum, UserRole

    init_db()

    #
    #  User1 setup
    #

    user = User(username='user1', password_hash=generate_password_hash('user1'),email='testMail@mail.com')
    module = Module(unique_id='unique_id_1', extraction_params=DEFAULT_EXTRACTION_PARAMS)
    user.modules.append(module)

    whitelist = Whitelist(name='debug_whitelist_1')
    user.whitelists.append(whitelist)

    for plate_text in ['WA6642E', 'WI027HJ', 'ERA75TM', 'ERA81TL', 'DBL6S01', 'DLU59AL', 'DLU36419']:
        whitelist.plates.append(Plate(text=plate_text))

    module.whitelists.append(whitelist)

    #
    # admin setup
    #

    admin_user_role = UserRole.query.filter_by(value=UserRoleEnum.Admin).first()
    admin = User(username='admin1', password_hash=generate_password_hash('admin1'), user_role=admin_user_role, email='admin@admin.com')

    for idx in range(2, 6):
        new_module = Module(unique_id=f'unique_id_{idx}')
        db.session.add(new_module)

    #
    # User2 setup
    #

    user2 = User(username='user2', email='user2@mail.com')
    user2.set_password('user2')

    whitelist_big = Whitelist(name='big_whitelist')
    user2.whitelists.append(whitelist_big)
    for i in range(10, 99):
        whitelist_big.plates.append(Plate(text='DBL6S' + str(i)))

    for i in range(1, 100):
        user2.whitelists.append(Whitelist(name='debug_whitelist_' + str(i)))

    for i in range(1, 100):
        user2.modules.append(Module(unique_id='debug_module_' + str(i)))

    db.session.add(user)
    db.session.add(admin)
    db.session.add(user2)

    db.session.commit()

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

    # this check for integrity of 'instance/photos' folder with database state
    @app.before_first_request
    def access_attempts_integrity_check():
            from ..models import AccessAttempt
            access_attempts = AccessAttempt.query.all()
            assert all(access_attempt.photos_exist() for access_attempt in access_attempts), \
                "There are access attempts without photos existing, please reinit db with 'flask init-db' or 'flask init-db-debug'"


@click.command('init-db-backup')
@click.argument('filename',default='database_backup')
@click.option('--verbose','-clean', is_flag=True,help='Clean backup dir')
@with_appcontext
def init_db_backup_command(filename,verbose):
    """Command for creating backup of database and processed images"""

    try:
        path = 'backup'

        if verbose and os.path.isdir(path):
            shutil.rmtree(path)

        if not os.path.isdir(path):
            os.mkdir(path)

        db_file = os.path.join(current_app.instance_path, 'rpiplatesrecognition.sqlite')
        backup_db_file = os.path.join(path, 'rpiplaterecognition' + time.strftime("-%Y%m%d-%H%M%S") + '.sqlite')

        shutil.copyfile(db_file, backup_db_file)
        print ("\nCreated database backup file: {}".format(backup_db_file))

        directory = os.path.join(current_app.instance_path, 'photos')
        photo_backup_dir = os.path.join(path, 'photos' + time.strftime("-%Y%m%d-%H%M%S"))
        shutil.copytree(directory, photo_backup_dir)
        print ("Created photo backup dir: {}".format(photo_backup_dir))

        backup_arch = filename + time.strftime("-%Y%m%d-%H%M%S")
        shutil.make_archive(backup_arch, 'tar', path)
        print ("Created database arch: {}.tar\n".format(backup_arch))
        shutil.rmtree(path)

    except Exception as error:
        print("Failed to create database backup")
        print(error)