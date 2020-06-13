from flask import render_template, request, Blueprint
from project1.model import Post


main = Blueprint('main', __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/home", methods=['GET', 'POST'])
def home():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)	
	return render_template("home.html", posts = posts)