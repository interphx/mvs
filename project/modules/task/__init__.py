from flask import render_template, abort

from project.rest import rest
from project.frontend import frontend

from .model import Task
from .resource import TaskAPI, TaskListAPI, UserTaskListAPI
from .schema import TaskSchema
from .views import *

rest.add_resource(TaskAPI, '/tasks/<int:id>/', endpoint='api.task')
rest.add_resource(TaskListAPI, '/tasks/', endpoint='api.tasks')
rest.add_resource(UserTaskListAPI, '/users/<int:user_id>/tasks/', endpoint='api.user_tasks')
