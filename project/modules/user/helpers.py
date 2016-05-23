import hashlib
import datetime
import project.mail as mail
import project.sms as sms
from flask import render_template
from flask.ext import login

from project import config
from project.database import db
from project.modules.user_contact import UserContact

from .model import User
from .passgen import gen_password, gen_salt

class EmailExistsException(Exception): pass
class InvalidEmailException(Exception): pass
class InvalidPasswordException(Exception): pass

# TODO: preferred_only
def notify_user(user, notification_means, preferred_only=True, subject='Уведомление'):
    for means, text in notification_means.items():
        if means == 'all':
            # TODO: Get preferred communication means
            notify_user(
                user=user, 
                notification_means=dict.fromkeys({'email', 'sms', 'pm'} - set(notification_means.keys()), text),
                preferred_only=preferred_only,
                subject=subject
            )
        elif means == 'email':
            if not user.email: continue
            mail.send_mail(
                subject=subject,
                body=text,
                sender = (config['website']['mail_name'], config['website']['mail_address']),
                recipients = [user.email]
            )
        elif means == 'sms':
            if not user.phone: continue
            sms.send_sms(
                phone=user.phone,
                text=text,
                test=False # TODO
            )
        elif means == 'pm':
            # TODO
            pass


def hash_password(password, salt):
    algo = config['accounts']['hashing_algorithm']
    if algo not in hashlib.algorithms_available:
        raise Exception('Invalid hashing algorithm: {}'.format(algo))

    pattern = config['accounts']['hashing_pattern']
    
    hasher = hashlib.new(algo)
    hasher.update(pattern.format(password=password, salt=salt).encode('utf-8'))
    return hasher.hexdigest()

def check_password(user, password):
    return hash_password(password, user.password_salt) == user.password

def login_user_object(user):
    result = login.login_user(user, **kwargs)
    if result:
        user.last_visited_at = datetime.datetime.utcnow()
        db.session.commit()
    return result

def login_user(email, password, **kwargs):
    user = User.query.filter_by(email=email).first()
    
    if not user:
        raise InvalidEmailException()
    if not check_password(user, password):
        raise InvalidPasswordException()
    
    result = login.login_user(user, **kwargs)
    #print('LOGGING IN: Result = {}'.format(result))
    if result:
        user.last_visited_at = datetime.datetime.utcnow()
        db.session.commit()
    return result

def set_user_password(user, raw_password):
    salt = gen_salt(config['accounts']['salt_length'])
    password_hash = hash_password(raw_password, salt)
    try:
        user.password_salt = salt
        user.password = password_hash
        db.session.commit()
    except:
        db.session.rollback()
        raise
    

def create_user(email, fullname, city, phone, password=None, send_email=True):
    if password == None:
        password = gen_password(config['accounts']['generated_password_length'])

    if User.query.filter_by(email=email).count() > 0:
        raise EmailExistsException('Email {} is already occupied'.format(email))

    salt = gen_salt(config['accounts']['salt_length'])

    password_hash = hash_password(password, salt)

    user = User(
        full_name = fullname,
        city = city,
        password = password_hash,
        password_salt = salt,
        email = email,
        phone = phone
    )
    
    email_contact = UserContact(
        type = 'email',
        value = email,
        owner = user
    )

    try:
        db.session.add(user)
        db.session.add(email_contact)
        db.session.commit()
    except:
        db.session.rollback()
        raise

    send_welcome_letter(email, password)

    return (user, password)

def send_confirmation_letter(email):
    # TODO
    pass

def send_welcome_letter(email, plain_password):
    text = render_template('letters/welcome.html',
        config = config,
        user_email = email,
        plain_password = plain_password
    )
    
    mail.send_mail(
        subject = "Добро пожаловать на {0}".format(config['website']['name']), 
        body = text, 
        sender = (config['website']['mail_name'], config['website']['mail_address']),
        recipients = [email]
    )