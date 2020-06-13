
from flask import render_template, flash, redirect, url_for, request, Blueprint
from project1 import db, bcrypt
from project1.model import User, Post
from project1.users.forms import (RegistrationForm, LoginForm, UserUpdateForm, 
							RequestResetForm, ResetPasswordForm)
from flask_login import login_user, current_user, logout_user, login_required
from project1.users.utils import save_image, send_reset_email

users = Blueprint('users', __name__)


@users.route("/login", methods=['GET', 'POST'])
def login():
	
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))

	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember = form.remember.data)
			next_page = request.args.get('next')
			if next_page:
				return redirect(next_page)
			else:
				return redirect(url_for('posts.post'))	
		else:
			flash('Login Unsuccessful.Please Check Email And Password!!', 'danger')
	return render_template("login.html", form = form)

@users.route("/register", methods=['GET', 'POST'])
def register():
	
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	
	form = RegistrationForm()
	if form.validate_on_submit():
		password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username= form.username.data, email = form.email.data, password = password )
		db.session.add(user)
		db.session.commit()
		flash(f'account created for {form.username.data}!', 'success')
		return redirect(url_for('users.login'))
	return render_template("signup.html", form = form)

@users.route("/logout")
def logout():

	logout_user()
	return redirect(url_for('main.index'))

@users.route("/account", methods=['GET', 'POST'])
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
		return redirect(url_for('users.account'))
	
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	name = url_for('static', filename = 'profile_pics/' + current_user.image_file)
	return render_template("account.html", name = name, form = form)

@users.route("/user_post/<string:username>", methods =['GET','POST'] )
@login_required
def user_post(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query\
		.filter_by(author=user)\
		.order_by(Post.date_posted.desc())\
		.paginate(page=page, per_page=5)
	return render_template("user_post.html", posts = posts, user = user)

@users.route("/request_reset", methods=['GET', 'POST'])
def request_reset():

	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent to reset your password', 'info')
		return redirect(url_for('users.login'))
	return render_template("reset_request.html", form = form)

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash("That is an invalid or expired token", 'warning')
		return redirect(url_for('users.request_reset'))
	form =ResetPasswordForm()
	if form.validate_on_submit():
		password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = password
		db.session.commit()
		flash(f'Your password has been updated!', 'success')
		return redirect(url_for('users.login'))
	return render_template("pwd_reset.html", form = form)