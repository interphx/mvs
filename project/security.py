from flask.ext import login

from project import app
from project.database import db
from project.modules.user import User, Anonymous
from project.modules.user_role import Role

login_manager = login.LoginManager()
login_manager.init_app(app)
login_manager.anonymous_user = Anonymous
login_manager.login_view = 'frontend.login'

@login_manager.user_loader
def load_user(id):
    print('USER LOADER CALLED')
    result = User.query.get( int(id) )
    print('REQUESTED USER ID: {}'.format(id))
    print('REQUESTED USER: {}'.format(result))
    return result

