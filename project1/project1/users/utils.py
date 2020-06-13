
import os
import secrets
from PIL import Image
from flask import url_for
from flask_mail import Message
from project1 import mail
from flask import current_app

def save_image(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(current_app.root_path,'static', 'profile_pics', picture_fn)

	output_size = (900, 900)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn

def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('password reset request', 
		sender = 'noreply@demo.com',
		recipients = [user.email])
	msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_password', token=token, _external=True)}

If you did not make this requeest then simply ignore this message and nothing will change  
'''
	mail.send(msg)
