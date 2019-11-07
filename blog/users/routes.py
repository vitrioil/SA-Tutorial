from blog import db, bcrypt
from blog.models import User, Post
from blog.users.utils import send_reset_email, save_picture
from flask import (render_template, flash, redirect, url_for, request,
                   Blueprint)
from blog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                              RequestResetForm, ResetPasswordForm)
from flask_login import login_user, current_user, logout_user, login_required


users = Blueprint("users", __name__)


@users.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data
                                                        ).decode()
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been created", category="success")
        return redirect(url_for("users.login"))
    return render_template("register.html", title="Register", form=form)


@users.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if (user and
                bcrypt.check_password_hash(user.password, form.password.data)):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next", "/main.home")[1:]
            return redirect(url_for(next_page))
        else:
            flash("Incorrect credentials!", category="danger")

    return render_template("login.html", title="Login", form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("users.login"))


@users.route('/account', methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            file_name = save_picture(form.picture.data)
            current_user.image = file_name
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated", category="success")
        return redirect(url_for("users.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image = url_for("static", filename=f"profile_pics/{current_user.image}")
    return render_template("account.html", title="Account",
                           image=image, form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=2)
    return render_template("user_posts.html", posts=posts, user=user)


@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("Email has been sent with instructions", category="info")
        return redirect(url_for("users.login"))
    return render_template("reset_request.html", form=form,
                           title="Reset Password")


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("Invalid or expired token!", category="warning")
        return redirect(url_for("users.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data
                                                        ).decode()
        user.password = hashed_password
        db.session.commit()
        flash(f"Your password has been updated!", category="success")
        return redirect(url_for("users.login"))
    return render_template("reset_token.html", form=form,
                           title="Reset Password")
