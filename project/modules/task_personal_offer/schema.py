from project.utils import json
from project.marshalling import ma

from project.modules.task import TaskSchema
from project.modules.user.schema import UserSchema

class TaskPersonalOfferSchema(ma.Schema):
    class Meta:
        json_module = json
        strict = True
        fields = (
            'id',
            'text',
            'created_at',
            'task',
            'sender',
            'receiver'
        )
    
    self_url = ma.Url(attribute='selfApiUrl')
    price = ma.Float()
    task = ma.Nested(TaskSchema, only=('id', 'title', 'status'))
    sender = ma.Nested(UserSchema, only=('id', 'full_name'))
    receiver = ma.Nested(UserSchema, only=('id', 'full_name'))