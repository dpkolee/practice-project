
from flask import render_template, flash, redirect, url_for, request, abort, Blueprint
from project1 import db
from project1.model import Post
from project1.posts.forms import UserPost
from flask_login import current_user, login_required


posts = Blueprint('posts', __name__)


@posts.route("/post", methods =['GET', 'POST'])
@login_required
def post():
	form = UserPost()
	if form.validate_on_submit():
		post = Post(title = form.title.data, content = form.content.data, author = current_user)
		db.session.add(post)
		db.session.commit()
		flash(f'Post created', 'success')
		return redirect(url_for('main.home'))
	return render_template("post.html", form=form, legend = "New Post")

@posts.route("/edit_post/<int:post_id>")
def edit_post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template("post_edit.html", post = post)

@posts.route("/edit_post/edit/<int:post_id>", methods =['GET', 'POST'] )
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = UserPost()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash(f'Post Updated', 'success')
		return redirect(url_for('main.home', post_id =post.id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template("post.html", form=form, post = post, legend= "Update Post")

@posts.route("/edit_post/delete/<int:post_id>", methods =['POST'] )
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash(f'Post deleted', 'success')
	return redirect(url_for('main.home'))