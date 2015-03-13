# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask.ext.login import login_required
from flask.ext.login import current_user
from sqlalchemy import asc, desc

from blogaggregator.user.forms import PostForm
from blogaggregator.user.forms import CommentForm
from blogaggregator.user.models import Post
from blogaggregator.user.models import User
from blogaggregator.user.models import Comment
from blogaggregator.utils import flash_errors
from blogaggregator.utils import summarise_post
from blogaggregator.utils import check_latest_update
from blogaggregator.database import db

from blogaggregator.user.forms import ProfileForm

from uuid import uuid4

blueprint = Blueprint("user", __name__, url_prefix='/users',
                        static_folder="../static")



@blueprint.route("/")
@login_required
def members():
    return render_template("users/members.html")

@blueprint.route("/profile",methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(request.form)
    if request.method == "GET": #populate registration form with the existing profile
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.registrationkey.data = "DS106TestKey"
        form.atomfeed.data = current_user.atomfeed
        form.password.data = current_user.password

    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.atomfeed = form.atomfeed.data
        current_user.set_password(form.password.data)
        db.session.commit()
        flash("Profile modified", 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
        
    return render_template("users/profile.html",user=current_user, form=form)

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
            title = form.title.data
            new_post = Post.create(content = content,
                summary = summary,
                title = title,
                user_id=current_user.id,
                atomuuid=str(uuid4()),
                link="")
            check_latest_update(current_user,new_post)
            flash("Thanks for the post.", 'success')
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
                
        #~ current_user.last_login=dt.datetime.now()   
        
    
    return render_template("users/addpost.html", form=form)

#TODO move this into the public views!
@blueprint.route("/posts/<username>/<postid>/", methods=["GET"])
def comment(username,postid):
    #~ form = CommentForm(request.form)
    allowedit = False # by default, no edits
    comments_all=db.session.query(Comment).filter(Comment.post_id==postid).order_by(asc(Comment.created_at)).all()
    if not comments_all :
        comments_all=[{'user':'username','content':'No comments yet :('}]
    else:  #check if the last post is byt he current user (for comment edits)
        last_comment_userid=comments_all[-1].user.id        
        if current_user.is_authenticated():
            if last_comment_userid == current_user.id:
                allowedit = True
    post = Post.query.get(postid)
    return render_template('users/comments.html',username=username,post=post,postid=postid,comments_all=comments_all, allowedit=allowedit)
    

# TODO fix, this doesn't also display the commments as it should    
@blueprint.route("/posts/<username>/<postid>/comment/<commentmethod>", methods=["POST","GET"])
@login_required
def makecomment(username,postid,commentmethod):
    #get the post owner user from url input
    post_owner = User.query.filter_by(username=username).first()
    
    
    if commentmethod == 'new':
        form = CommentForm(request.form)
    elif commentmethod == 'edit':
        comment_last=db.session.query(Comment).filter(Comment.post_id==postid).order_by(desc(Comment.created_at)).first()
        # if the current user is the one who made the last comment, allow editing
        if comment_last.user_id == current_user.id:
            old_content=comment_last.content
            row={'comment':old_content}
            form = CommentForm(**row)
        else:
            flash("Sorry you cannot edit this post","warning")
            redirect_url =  url_for('user.comment',username=username, postid=postid)
    else: #invalid var passed to url builder
        redirect_url =  url_for('user.comment',username=username, postid=postid)
        return redirect(redirect_url)
    
    if request.method == "GET":
        pass
    if request.method == "POST":
        if form.validate_on_submit:
            comment = form.comment.data
            if commentmethod == 'new':
                new_comment = Comment.create(content=form.comment.data,
                    post_id = postid,
                    user_id = current_user.id)
                
                check_latest_update(post_owner,new_comment)
                #update count on posts
                post=Post.query.filter_by(id = postid).first()
                comment_count=db.session.query(Comment).filter(Comment.post_id==postid).order_by(asc(Comment.created_at)).count()
                post.comment_count=comment_count
                flash("Thanks for making a comment.", 'success')
            elif commentmethod == 'edit':
                comment_last.content = comment
                check_latest_update(post_owner,comment_last)
                flash("Comment edited.", 'success')
            db.session.commit()
            
            redirect_url =  url_for('user.comment',username=username, postid=postid)
            return redirect(redirect_url)
        else:
            flash_errors(form)
            redirect_url =  url_for('user.comment',username=username, postid=postid)
            return redirect(redirect_url)
    return render_template('users/newcomment.html',form=form)

