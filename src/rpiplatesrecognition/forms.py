import re

from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.simple import TextAreaField
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

'''
PLATE_RE = re.compile(r'^[A-Z]{2,3}[A-Z0-9]{4,5}$')

class EditWhitelistForm(FlaskForm):
    def __init__(self, whitelist: Whitelist):
        FlaskForm.__init__(self)
        for plate in whitelist.plates:
            if self.plates.data:
                self.plates.data += plate.text + '\n'
            else:
                self.plates.data = plate.text + '\n'

    plates = TextAreaField('Plates in whitelist', validators=[DataRequired()])
    submit = SubmitField('Process changes', validators=[DataRequired()])

    def validate_plates(self, plates):
        for line in plates.data.split('\n'):
            stripped = line.rstrip()
            if not (7 <= len(stripped) and len(stripped) <= 8):
                raise ValidationError(f'Invalid plate length: {stripped}({len(stripped)})')
            if re.match(PLATE_RE, stripped) is None:
                raise ValidationError(f'Plate: {stripped} doesn\'t match regex')
'''
