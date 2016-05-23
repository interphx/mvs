from flask import Blueprint, render_template
from flask.ext.login import login_required

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
def index():
    return render_template('main.html')

@frontend.route('access_denied')
def access_denied():
    return render_template('error/access_denied.html')