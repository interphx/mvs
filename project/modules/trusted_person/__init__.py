from project.rest import rest

from .model import *
from .resource import *
from .schema import *

rest.add_resource(TrustedPersonAPI, '/trusted_person/<int:id>/', endpoint='api.trusted_person')
rest.add_resource(TrustedPersonListAPI, '/trusted_persons/', endpoint='api.trusted_persons')