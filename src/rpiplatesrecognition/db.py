import click
from flask import current_app, Flask
from flask.app import Flask
from flask.cli import with_appcontext

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db():
    db.drop_all()
    db.create_all()

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized db')

def init_app(app: Flask):
    db.init_app(app)
    app.cli.add_command(init_db_command)
