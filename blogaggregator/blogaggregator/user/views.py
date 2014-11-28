# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask.ext.login import login_required
from flask.ext.login import current_user

from blogaggregator.user.forms import PostForm
from blogaggregator.user.models import Post
from blogaggregator.utils import flash_errors
from blogaggregator.utils import summarise_post

from uuid import uuid4

blueprint = Blueprint("user", __name__, url_prefix='/users',
                        static_folder="../static")


@blueprint.route("/")
@login_required
def members():
    return render_template("users/members.html")

@blueprint.route("/addpost/", methods=["GET","POST"])
@login_required
def addpost():
    form = PostForm(request.form)
    if request.method == "GET":  #save current written data in the session TODO do this
        pass 
    
    if request.method == 'POST':
        if form.validate_on_submit:
            content = form.content.data
            summary = summarise_post(content)
            new_post = Post.create(content = content,
                summary = summary,
                user_id=current_user.id,
                atomuuid=str(uuid4()),
                link="")
            flash("Thanks for the post.", 'success')
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
                
        #~ current_user.last_login=dt.datetime.now()   
        
    
    return render_template("users/addpost.html", form=form)
