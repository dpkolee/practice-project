
import os

class Config:

	SECRET_KEY = '635d7ebbe888a52c584a27c64374daeb'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get('EMAIL')
	MAIL_PASSWORD = 'vxzobgcejjhirrjj'