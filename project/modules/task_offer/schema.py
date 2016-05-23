from project.utils import json
from project.marshalling import ma

from project.modules.task import TaskSchema
from project.modules.user.schema import UserSchema

class TaskOfferSchema(ma.Schema):
    class Meta:
        json_module = json
        strict = True
        fields = (
            'id',
            'text',
            'created_at',
            'task',
            'doer',
            'price'
        )
    
    self_url = ma.Url(attribute='selfApiUrl')
    price = ma.Float()
    task = ma.Nested(TaskSchema, only=('id', 'title', 'status'))
    doer = ma.Nested(UserSchema, only=('id', 'full_name', 'age'))