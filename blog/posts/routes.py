from blog import db
from flask import Blueprint
from blog.models import Post
from blog.posts.forms import PostForm
from flask_login import current_user, login_required
from flask import (render_template, flash, redirect, url_for, request,
                   abort)
posts = Blueprint("posts", __name__)


@posts.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data,
                    author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post is created!", category="success")
        return redirect(url_for("main.home"))
    return render_template("create_post.html", title="New Post", form=form,
                           legend="New Post")


@posts.route("/post/<int:post_id>")
def post(post_id: int):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)


@posts.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id: int):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated!", category="success")
        return redirect(url_for("posts.post", post_id=post_id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    form.title.data = post.title
    form.content.data = post.content
    return render_template("create_post.html", title="Update Post",
                           form=form, legend="Update Post")


@posts.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id: int):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted", category="success")
    return redirect(url_for("main.home"))
