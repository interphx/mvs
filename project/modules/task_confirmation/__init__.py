from project.rest import rest

from .model import TaskConfirmation
from .resource import TaskConfirmationListAPI

rest.add_resource(TaskConfirmationListAPI, '/task_confirmations/', endpoint='api.task_confirmations')