import re

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed, FileField
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from .models import User, Module, Whitelist

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign In')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username')


class AddModuleForm(FlaskForm):
    unique_id = StringField('Unique id', validators=[DataRequired()])
    submit = SubmitField('Add')

    def validate_unique_id(self, unique_id):
        module = Module.query.filter_by(unique_id=unique_id.data).first()

        if module is None:
            raise ValidationError('Unknown unique id')

        if module.user is not None:
            raise ValidationError('Module is already registed to a user')


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('Password', validators=[DataRequired()])
    new_password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change password')


class AddWhitelistForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add a whitelist')


class UploadImageForm(FlaskForm):
    file = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg'], 'Only jpg images!')])
    submit = SubmitField('Add an access attempt')

class AddWhitelistForm(FlaskForm):
    whitelist_name = StringField('Whitelist name', validators=[DataRequired()])
    submit = SubmitField('Add whitelist')

    def validate_whitelist_name(self, whitelist_name):
        whitelist = Whitelist.query.filter_by(name=whitelist_name.data).first()

        if whitelist is not None:
            raise ValidationError('This name is already taken')
        
        if len(whitelist_name.data) < 2:
            raise ValidationError('Too short name')

