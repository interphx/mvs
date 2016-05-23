from project.rest import rest

from .model import *
from .views import *
from .resource import *

rest.add_resource(UserAPI, '/users/<int:id>/', endpoint='api.user')
rest.add_resource(UserPasswordChangeAPI, '/users/<int:id>/password_change/', endpoint='api.user_password_change')
#rest.add_resource(UserListAPI, '/users/', endpoint='api.users')