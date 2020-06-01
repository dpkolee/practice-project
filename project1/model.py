
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):

	__tablename__ = "user"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	email = db.Column(db.String, nullable=False)
	password = db.Column(db.String, nullable=False)

class Book(db.Model):

	__tablename__ = "book"
	id = db.Column(db.Integer, primary_key=True)
	isbn = db.Column(db.Integer, nullable=False)
	title = db.Column(db.String, nullable=False)
	author = db.Column(db.String, nullable=False)
	year = db.Column(db.Integer, nullable=False)


		