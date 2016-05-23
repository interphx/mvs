from project.rest import rest

from .model import *
from .resource import *
from .schema import *

rest.add_resource(PrivateMessageAPI, '/pms/<int:id>/', endpoint='api.pm')
rest.add_resource(PrivateMessageListAPI, '/pms/', endpoint='api.pms')