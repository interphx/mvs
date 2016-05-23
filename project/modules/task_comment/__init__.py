from project.rest import rest

from .model import TaskComment
from .resource import TaskCommentAPI, TaskCommentListAPI
from .schema import TaskSchema

rest.add_resource(TaskCommentAPI, '/task_comments/<int:id>/', endpoint='api.task_comment')
rest.add_resource(TaskCommentListAPI, '/task_comments/', endpoint='api.task_comments')
