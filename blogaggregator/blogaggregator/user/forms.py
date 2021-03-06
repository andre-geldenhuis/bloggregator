from flask_wtf import Form
from wtforms import TextField, PasswordField, TextAreaField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, Email, EqualTo, Length, url
from blogaggregator.utils import good_feed
from flask.ext.login import current_user


from .models import User

class RegisterForm(Form):
    username = TextField('Username',
                    validators=[DataRequired(), Length(min=3, max=25)])
    email = TextField('Email',
                    validators=[DataRequired(), Email(), Length(min=6, max=40)])
    atomfeed = URLField('Atom Feed')
    registrationkey = TextField('Registration Key',validators=[DataRequired()])
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
        if self.registrationkey.data != "DS106TestKey":
            self.registrationkey.errors.append("Please enter the correct registration key")
            return False
        #only check if there is a string in self.atomfeed.data, that way users
        #can elect to not enter a atom feed.
        if self.atomfeed.data: 
            if not good_feed(self.atomfeed.data):
                print "data is:" + self.atomfeed.data + ":"
                self.atomfeed.errors.append("Bad atom feed, please try again")
                return False
        
        return True

class ProfileForm(RegisterForm):
    
    username = TextField('Username')
    
    #define custom validator to allow user to keep their username and email the same
    #TODO this validate routine users so much of the RegisterForm one
    #fix it to have less code repetition 
    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        
        if current_user.email != self.email.data:
            user = User.query.filter_by(email=self.email.data).first()
            if user:
                self.email.errors.append("Email already registered")
                return False
                
        #only check if there is a string in self.atomfeed.data, that way users
        #can elect to not enter a atom feed.
        if self.atomfeed.data: 
            if not good_feed(self.atomfeed.data):
                print "data is:" + self.atomfeed.data + ":"
                self.atomfeed.errors.append("Bad atom feed, please try again")
                return False
        
        return True

class PostForm(Form):
    title = TextField('Title',
                    validators=[DataRequired(), Length(min=3, max=125)])
    content = TextAreaField('Comment',validators=[DataRequired(), Length(min=3, max=25)])
    
    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            self.username.errors.append("Failed vaildation")
            return False
        return True

class CommentForm(Form):
    comment = TextAreaField('Comment',validators=[DataRequired(), Length(min=3, max=25)])
    
    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            self.username.errors.append("Failed vaildation")
            return False
        return True
