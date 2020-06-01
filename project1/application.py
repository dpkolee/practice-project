import os
import csv
from flask import Flask, session,  render_template, request, flash, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from model import *
from form import RegistrationForm, LoginForm

app = Flask(__name__)

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
#   raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config['SECRET_KEY'] = 'd2345c0e99d241787553c933368ead97'

db.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		if form.email.data == "deepakolee@gmail.com" and form.password.data == "password":
			flash('Logged In', 'success')
			return redirect(url_for('index'))
		else:
			flash('Login Unsuccessful.Please Check Username And Password!!', 'danger')
	return render_template("login.html", form = form)

@app.route("/register", methods=["GET", "POST"])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		flash(f'account created for {form.username.data}!', 'success')
		return redirect(url_for('login'))
	return render_template("signup.html", form = form)

def main():
	#db.create_all()
	f = open("books.csv")
	reader = csv.reader(f)
	for isbn, title, author, year in reader:
		book = Book(isbn=isbn, title=title, author=author, year=year)
		db.session.add(book)
		print(f"{isbn},{author},{title},{year}")
		db.session.commit()

if __name__ == "__main__":

	app.run(debug = True)
	
	with app.app_context():
		main()
