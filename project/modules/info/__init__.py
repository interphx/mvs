from flask import render_template, abort

from project.rest import rest
from project.frontend import frontend

from .views import *
from .resource import *

rest.add_resource(InfoPageAPI, '/info/<int:id>/', endpoint='api.info_page')
rest.add_resource(InfoPageListAPI, '/info/', endpoint='api.info_pages')