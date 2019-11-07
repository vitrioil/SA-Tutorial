from flask import Blueprint
from blog.models import Post
from flask import render_template, request
main = Blueprint("main", __name__)


@main.route('/', methods=["GET"])
@main.route("/home")
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc())\
                .paginate(page=page, per_page=2)
    return render_template("index.html", posts=posts)
