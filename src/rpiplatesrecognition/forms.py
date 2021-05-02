import re

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed, FileField
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.core import RadioField, SelectMultipleField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from wtforms.widgets.core import Select, SubmitInput

from .models import User, Module, Whitelist, Plate
from .db.helpers import get_modules_for_user_query, get_whitelists_for_user_query

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


class AddModuleFormAjax(AddModuleForm):
    submit = None


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
    whitelist_name = StringField('Whitelist name', validators=[DataRequired(),Length(2)])
    submit = SubmitField('Add whitelist')

    def validate_whitelist_name(self, whitelist_name):
        whitelist = Whitelist.query.filter_by(name=whitelist_name.data).first()

        if whitelist is not None:
            raise ValidationError('This name is already taken')


class AddPlateForm(FlaskForm):
    plate = StringField('Plate', validators=[DataRequired()], render_kw={'placeholder': 'Plate...'})
    whitelist_id = HiddenField('whitelist_id', validators=[DataRequired()])

    def validate_whitelist_id(self, whitelist_id):
        whitelist = get_whitelists_for_user_query(current_user).filter(Whitelist.id == whitelist_id.data).first()

        if whitelist is None:
            raise ValidationError('Wrong whitelist id')

    def validate_plate(self, plate):
        if not Plate.is_valid_plate(plate.data):
            raise ValidationError('Plate does not comply to policy')

        possible_plate = (Whitelist.query
            .join(Plate, Whitelist.id == Plate.whitelist_id)
            .filter(Whitelist.id == self.whitelist_id.data)
            .filter(Plate.text == plate.data)).first()

        if possible_plate is not None:
            raise ValidationError('Plate already in a whitelist')


def whitelist_id_to_whitelist(whitelist_id: int):
    return get_whitelists_for_user_query(current_user).filter(Whitelist.id == whitelist_id).first()


def BindWhitelistToModuleDynamicCtor(user: User):
    class Form(FlaskForm):
        pass

    for module in user.modules:
        form_name = f'{module.unique_id}_whitelists'

        users_whitelists = [(whitelist.id, whitelist.name) for whitelist in user.whitelists]

        setattr(Form, form_name, SelectMultipleField(
            'Select whitelists',
            choices=users_whitelists,
            default=[whitelist.id for whitelist in module.whitelists],
            coerce=int,
            render_kw={"class": "selectpicker"}))

        def validate(self, field):
            if not all(whitelist is not None for whitelist in field.data):
                raise ValidationError('Wrong whitelists')

        setattr(Form, 'validate_' + form_name, validate)

    return Form()
