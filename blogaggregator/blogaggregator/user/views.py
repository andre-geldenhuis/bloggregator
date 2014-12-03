# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask.ext.login import login_required
from flask.ext.login import current_user
from sqlalchemy import asc

from blogaggregator.user.forms import PostForm
from blogaggregator.user.forms import CommentForm
from blogaggregator.user.models import Post
from blogaggregator.user.models import Comment
from blogaggregator.utils import flash_errors
from blogaggregator.utils import summarise_post
from blogaggregator.database import db

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

@blueprint.route("/posts/<username>/<postid>/", methods=["GET","POST"])
@login_required
def comment(username,postid):
    form = CommentForm(request.form)
    if request.method == "GET":
        comments_all=db.session.query(Comment).filter(Comment.post_id==postid).order_by(asc(Comment.created_at)).all()
        if comments_all == None:
            comments_all=[{'content':'No comments yet :('}]
    
    if request.method == "POST":
        if form.validate_on_submit:
            comment = form.comment.data
            new_comment = Comment.create(content=form.comment.data,
                post_id=postid,
                user_id=current_user.id)
            #update count on posts
            post=Post.query.filter_by(id=postid).first()
            comment_count=db.session.query(Comment).filter(Comment.post_id==postid).order_by(asc(Comment.created_at)).count()
            post.comment_count=comment_count
            db.session.commit()
            flash("Thanks for making a comment.", 'success')
            redirect_url =  url_for('user.comment',username=username, postid=postid)
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template('users/comments.html',form=form,comments_all=comments_all)
