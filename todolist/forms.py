from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, EmailField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from todolist.models import User, List, Task
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2,max=30)])
    email = EmailField('Email Id', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords should match!")])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(name = username.data).first()
        if user:
            raise ValidationError('This username already exists!!! Try a new one.')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('This email already exists!!! Try a new one.')


class LoginForm(FlaskForm):
    email = EmailField('Email Id', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign In')

class ListForm(FlaskForm):
    title = StringField('List Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    is_important = BooleanField('Mark as Important')
    color = SelectField('Pick a color', choices=[])
    submit = SubmitField('Create')

    def validate_title(self, title):
        new_list = List.query.filter_by(title = title.data).filter(List.user_id == current_user.id).first()
        if new_list:
            raise ValidationError('This list name already exists!!! Try a new one.')

class ListUpdateForm(FlaskForm):
    title = StringField('List Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    is_important = BooleanField('Mark as Important')
    color = SelectField('Pick a color', choices=[])
    submit = SubmitField('Update')

class TaskForm(FlaskForm):
    content = StringField('Enter new task here:', validators=[DataRequired()])
    submit = SubmitField('Add')
    

class AccountUpdateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2,max=30)])
    email = EmailField('Email Id', validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.name:
            user = User.query.filter_by(name = username.data).first()
            if user:
                raise ValidationError('This username already exists!!! Try a new one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError('This email already exists!!! Try a new one.')

class SearchTaskForm(FlaskForm):
    searchText = StringField('Search task here', validators=[DataRequired()])
    submit = SubmitField('Search')
