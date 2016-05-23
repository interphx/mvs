from project.rest import rest

from .model import *
from .resource import *
from .views import *

rest.add_resource(UploadListAPI, '/uploads/', endpoint='api.uploads')
rest.add_resource(WysiwygUploadAPI, '/wysiwyg_uploads/', endpoint='api.wysiwyg_uploads')