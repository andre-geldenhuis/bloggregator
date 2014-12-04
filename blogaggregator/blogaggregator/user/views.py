# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask.ext.login import login_required
from flask.ext.login import current_user
from sqlalchemy import asc, desc

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

#TODO move this into the public views!
@blueprint.route("/posts/<username>/<postid>/", methods=["GET"])
def comment(username,postid):
    #~ form = CommentForm(request.form)
    allowedit = False # by default, no edits
    comments_all=db.session.query(Comment).filter(Comment.post_id==postid).order_by(asc(Comment.created_at)).all()
    if comments_all == None:
        comments_all=[{'content':'No comments yet :('}]
    else:  #check if the last post is byt he current user (for comment edits)
        last_comment_userid=comments_all[-1].user.id
        if last_comment_userid == current_user.id:
            allowedit = True
    return render_template('users/comments.html',username=username,postid=postid,comments_all=comments_all, allowedit=allowedit)
    

# TODO fix, this doesn't also display the commments as it should    
@blueprint.route("/posts/<username>/<postid>/comment", methods=["POST","GET"])
@login_required
def makecomment(username,postid):
    form = CommentForm(request.form)
    if request.method == "GET":
        pass
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
            redirect_url =  url_for('user.comment',username=username, postid=postid)
            return redirect(redirect_url)
    return render_template('users/newcomment.html',form=form)

# TODO modify this for code reuse!  really similar to makecomment
@blueprint.route("/posts/<username>/<postid>/editcomment", methods=["POST","GET"])
@login_required
def editcomment(username,postid):
    # Check if user is still allowed to make edit
    allowedit = False # by default, no edits
    comment_last=db.session.query(Comment).filter(Comment.post_id==postid).order_by(desc(Comment.created_at)).first()
    if comment_last.user_id == current_user.id :
        old_content=comment_last.content
        row={'comment':old_content}
        form = CommentForm(**row)
        if request.method == "GET":
            pass
            
        if request.method == "POST":
            if form.validate_on_submit:
                commentedit = form.comment.data
                comment_last.content=commentedit
                db.session.commit()
                flash("Comment edited.", 'success')
                redirect_url =  url_for('user.comment',username=username, postid=postid)
                return redirect(redirect_url)
            else:
                flash_errors(form)
                redirect_url =  url_for('user.comment',username=username, postid=postid)
                return redirect(redirect_url)
        return render_template('users/editcomment.html',form=form)
    
    else:
        flash("Sorry you cannot edit this post","warning")
        redirect_url =  url_for('user.comment',username=username, postid=postid)
        
    
    
