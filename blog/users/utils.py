import os
import secrets
from blog import mail
from PIL import Image
from flask import url_for
from flask_mail import Message
from flask import current_app as app


def save_picture(picture):
    name = secrets.token_hex(8)
    _, extension = os.path.splitext(picture.filename)
    file_name = name + extension
    picture_path = os.path.join(app.root_path,
                                "static/profile_pics", file_name)
    output_size = (125, 125)
    '''
    s = request.files['picture'].read()
    i = np.fromstring(s)
    img = cv2.imdecode(i, flag
    '''
    i = Image.open(picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return file_name


def send_reset_email(user):
    token = user.get_reset_token(expires_sec=1800)
    msg = Message("Password Reset Request", sender="noreply@g.com",
                  recipients=[user.email])
    msg.body = f''' To reset password visit:
{url_for('reset_token', token=token, _external=True)}

If you didn't request, don't change anything!
    '''
    mail.send(msg)
