from project.rest import rest

from .model import Category
from .resource import *
from .schema import *
from .schema_tasks import *

rest.add_resource(CategoryAPI, '/cats/<url_name>/', endpoint='api.category')
rest.add_resource(CategoryTasksAPI, '/cats/<url_name>/tasks/', endpoint='api.category_tasks')
rest.add_resource(CategoryListAPI, '/cats/', endpoint='api.categories')