import os
import secrets
from PIL import Image
from flask import render_template, flash, redirect, url_for, request, abort
from project1 import app, db, bcrypt, mail
from project1.model import User, Post
from project1.form import (RegistrationForm, LoginForm, UserUpdateForm, 
							UserPost, RequestResetForm, ResetPasswordForm)
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home", methods=['GET', 'POST'])
def home():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)	
	return render_template("home.html", posts = posts)

@app.route("/login", methods=['GET', 'POST'])
def login():
	
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember = form.remember.data)
			next_page = request.args.get('next')
			if next_page:
				return redirect(next_page)
			else:
				return redirect(url_for('post'))	
		else:
			flash('Login Unsuccessful.Please Check Email And Password!!', 'danger')
	return render_template("login.html", form = form)

@app.route("/register", methods=['GET', 'POST'])
def register():
	
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	
	form = RegistrationForm()
	if form.validate_on_submit():
		password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username= form.username.data, email = form.email.data, password = password )
		db.session.add(user)
		db.session.commit()
		flash(f'account created for {form.username.data}!', 'success')
		return redirect(url_for('login'))
	return render_template("signup.html", form = form)

@app.route("/logout")
def logout():

	logout_user()
	return redirect(url_for('index'))

def save_image(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path,'static', 'profile_pics', picture_fn)

	output_size = (900, 900)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn



@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UserUpdateForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_image(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('your account has been updated!', 'success')
		return redirect(url_for('account'))
	
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	name = url_for('static', filename = 'profile_pics/' + current_user.image_file)
	return render_template("account.html", name = name, form = form)

@app.route("/post", methods =['GET', 'POST'])
@login_required
def post():
	form = UserPost()
	if form.validate_on_submit():
		post = Post(title = form.title.data, content = form.content.data, author = current_user)
		db.session.add(post)
		db.session.commit()
		flash(f'Post created', 'success')
		return redirect(url_for('home'))
	return render_template("post.html", form=form, legend = "New Post")

@app.route("/edit_post/<int:post_id>")
def edit_post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template("post_edit.html", post = post)

@app.route("/edit_post/edit/<int:post_id>", methods =['GET', 'POST'] )
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
		return redirect(url_for('home', post_id =post.id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template("post.html", form=form, post = post, legend= "Update Post")

@app.route("/edit_post/delete/<int:post_id>", methods =['POST'] )
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash(f'Post deleted', 'success')
	return redirect(url_for('home'))

@app.route("/user_post/<string:username>", methods =['GET','POST'] )
@login_required
def user_post(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query\
		.filter_by(author=user)\
		.order_by(Post.date_posted.desc())\
		.paginate(page=page, per_page=5)
	return render_template("user_post.html", posts = posts, user = user)

def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('password reset request', 
		sender = 'noreply@demo.com',
		recipients = [user.email])
	msg.body = f'''To reset your password, visit the following link:
{url_for('reset_password', token=token, _external=True)}

If you did not make this requeest then simply ignore this message and nothing will change  
'''
	mail.send(msg)

@app.route("/request_reset", methods=['GET', 'POST'])
def request_reset():

	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent to reset your password', 'info')
		return redirect(url_for('login'))
	return render_template("reset_request.html", form = form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash("That is an invalid or expired token", 'warning')
		return redirect(url_for('request_reset'))
	form =ResetPasswordForm()
	if form.validate_on_submit():
		password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = password
		db.session.commit()
		flash(f'Your password has been updated!', 'success')
		return redirect(url_for('login'))
	return render_template("pwd_reset.html", form = form)