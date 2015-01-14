# -*- coding: utf-8 -*-
'''Public section, including homepage and signup.'''
from flask import (Blueprint, request, render_template, flash, url_for,
                    redirect, session)
from flask.ext.login import login_user, login_required, logout_user
from sqlalchemy import desc

from blogaggregator.extensions import login_manager
from blogaggregator.user.models import User
from blogaggregator.user.models import Post
from blogaggregator.public.forms import LoginForm
from blogaggregator.user.forms import RegisterForm
from blogaggregator.utils import flash_errors
from blogaggregator.database import db

from bleach import clean


class NoPosts:          
    def __init__( self, user ):
        self.user = user
        self.summary = "No Posts :("

blueprint = Blueprint('public', __name__, static_folder="../static")

@login_manager.user_loader
def load_user(id):
    return User.get_by_id(int(id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    form = LoginForm(request.form)
    
    #get all the users who exist
    allusers=User.query.all()
    postlist=[]
    for user in allusers:
        latestpost_object = Post.query.filter_by(user_id=user.id).order_by(desc(Post.created_at)).limit(1).first()
        if latestpost_object == None:
            latestpost = NoPosts(user)
        else:
            latestpost = latestpost_object
            
        postlist.append(latestpost)
    
    #sort postlist by latest post or comment IF there are any posts
    if len(postlist) == 1 and postlist[0] == "":
        pass
    else:
        postlist.sort(key = lambda x: x.user.latest_update, reverse=True)
    
    # Handle loggin
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", 'success')
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/home.html", form=form, postlist=postlist)

@blueprint.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('User %s not found!' % username,'warning')
        return redirect(url_for('public.home'))

    posts_all=db.session.query(Post).filter(Post.user_id==user.id).order_by(desc(Post.created_at)).all()
    return render_template('public/user.html',
                           user=user,
                           posts=posts_all)


@blueprint.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))

@blueprint.route("/register/", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        new_user = User.create(username=form.username.data,
                        email=form.email.data,
                        atomfeed=form.atomfeed.data,
                        password=form.password.data,
                        active=True)
        flash("Thank you for registering. You can now log in.", 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)

@blueprint.route("/about/")
def about():
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)
