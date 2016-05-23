from project.utils import json
from project.marshalling import ma
from project.modules.task.schema import TaskSchema

class CategoryTasksSchema(ma.Schema):
    class Meta:
        json_module = json
        strict = True
        fields = (
            'items',
            'category_url',
            'self_url'
        )
    
    test = ma.String('132323')
    items = ma.Nested(TaskSchema, only=('id', 'title', 'self_url'), many=True)
    category_url = ma.Url()
    self_url = ma.Url()