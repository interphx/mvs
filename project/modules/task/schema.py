from project.utils import json
from project.marshalling import ma
from project.modules.category.schema import CategorySchema

class TaskSchema(ma.Schema):
    class Meta:
        json_module = json
        strict = True
        fields = (
            'id',
            'title',
            'description',
            'created_at',
            'due',
            'contacts',
            'addresses',
            'reward',
            'status',
            'additional_data',
            'category',
            'self_url'
        )
    
    self_url = ma.Url(attribute='selfApiUrl')
    reward = ma.Float()
    category = ma.Nested(CategorySchema)
    #customer = ma.Nested(TaskStatusEnumSchema, exclude=('created_tasks',))
    #customer = db.Nested()

class TaskListSchema(ma.Schema):
    class Meta:
        json_module = json
        strict = True
        fields = (
            'tasks',
        )
    tasks = ma.Nested(TaskSchema, only=('id', 'title', 'status'), many=True)