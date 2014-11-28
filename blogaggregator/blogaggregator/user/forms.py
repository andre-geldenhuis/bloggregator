from flask_wtf import Form
from wtforms import TextField, PasswordField, TextAreaField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, Email, EqualTo, Length, url


from .models import User

class RegisterForm(Form):
    username = TextField('Username',
                    validators=[DataRequired(), Length(min=3, max=25)])
    email = TextField('Email',
                    validators=[DataRequired(), Email(), Length(min=6, max=40)])
    atomfeed = URLField(validators=[url()])
    password = PasswordField('Password',
                                validators=[DataRequired(), Length(min=6, max=40)])
    confirm = PasswordField('Verify password',
                [DataRequired(), EqualTo('password', message='Passwords must match')])

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append("Username already registered")
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True

class PostForm(Form):
    title = TextField('Title',
                    validators=[DataRequired(), Length(min=3, max=125)])
    content = TextAreaField('Comment',validators=[DataRequired(), Length(min=3, max=25)])
    summary = TextAreaField('Comment') 
    
    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            self.username.errors.append("Failed vaildation")
            return False
        return True
