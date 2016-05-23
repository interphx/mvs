from project.utils import json
from project.marshalling import ma

from project.modules.task import TaskSchema
from project.modules.user.schema import UserSchema

class TaskCommentSchema(ma.Schema):
    class Meta:
        json_module = json
        strict = True
        fields = (
            'id',
            'text',
            'created_at',
            'task',
            'author',
        )
    
    self_url = ma.Url(attribute='selfApiUrl')
    reward = ma.Float()
    task = ma.Nested(TaskSchema, only=('id', 'title', 'status'))
    author = ma.Nested(UserSchema, only=('id', 'full_name', 'age'))
    #customer = ma.Nested(TaskStatusEnumSchema, exclude=('created_tasks',))
    #customer = db.Nested()