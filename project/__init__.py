# -*- coding: utf-8 -*-
import json
import project.util
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

CONFIG_LOCATION = 'config/config.json'
DEFAULT_CONFIG_LOCATION = 'config/default.json'

#==============================================================================
# Configuration
#==============================================================================

with open(DEFAULT_CONFIG_LOCATION, 'r') as f:
    default_config = json.load(f)

with open(CONFIG_LOCATION, 'r') as f:
    config = json.load(f)

util.mergeDicts(config, default_config)

STATIC_FILES_LOCATION = '../' + config['app']['static_dir']

app = Flask(
    __name__,
    template_folder='../' + config['app']['template_dir'],
    static_folder=STATIC_FILES_LOCATION
)

app.config['SQLALCHEMY_DATABASE_URI'] = config['app']['database_uri']
app.config.update(config['flask'])

#==============================================================================
# Logging
#==============================================================================

import logging
logging.basicConfig(filename='movesol_flask_error.log', level=logging.DEBUG)

#==============================================================================
# CSRF protection
#==============================================================================

from flask_wtf.csrf import CsrfProtect

csrf = CsrfProtect()
csrf.init_app(app)

#==============================================================================
# Database initialization
#==============================================================================

db = SQLAlchemy(app)

#==============================================================================
# Login management
#==============================================================================

import project.security

#==============================================================================
# Marshmallow initialization
#==============================================================================

import project.marshalling

#==============================================================================
# Blueprints and API registration
#==============================================================================

from project.rest import rest
from project.frontend import frontend

#==============================================================================
# Modules loading
#==============================================================================

import project.module_loader

app.register_blueprint(frontend, url_prefix='/')

#==============================================================================
# Create DB tables
#==============================================================================

db.create_all()

#==============================================================================
# Add jinja2 custom filters and globals
#==============================================================================

import project.template_globals

#==============================================================================
# Debug
#==============================================================================

from project.modules.category import Category
from project.modules.user import User

#util.createIfNone(db.session, UserContactTypeEnum, name='email')
#util.createIfNone(db.session, UserContactTypeEnum, name='phone')
#util.createIfNone(db.session, UserContactTypeEnum, name='vk')
#util.createIfNone(db.session, UserContactTypeEnum, name='facebook')
#util.createIfNone(db.session, UserContactTypeEnum, name='mail.ru')
#util.createIfNone(db.session, UserContactTypeEnum, name='twitter')

db.session.commit()

if Category.query.count() < 1:
    all = Category(
        name="Все задания",
        url_name='all',
        parent=None
    )
    db.session.add(all)
    
    cour = Category(name="Курьерские услуги", parent=all)
    db.session.add(cour)
    
    db.session.add(
        Category(name="Услуги пешего курьера", parent=cour)
    )

    db.session.commit()

if User.query.count() < 1:
    import hashlib
    salt = "saltsalt"
    password = "qwerty"
    pwdhash = hashlib.sha1((salt + password).encode('utf-8')).hexdigest()

    util.createIfNone(db.session, User,
        full_name="Вася Васин",
        password_salt=salt,
        password=pwdhash,
        city="Караганда",
        active=True
    )
    db.session.commit()


'''
import project.mail
project.mail.send_mail(
    "Movesol server is now online",
    "Congratulations! Movesol server is now online",
    sender=(config['website']['mail_name'], config['website']['mail_address']),
    recipients=['guest-mail@yandex.ru']
)'''