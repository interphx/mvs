from project.utils import json
from project.marshalling import ma
from marshmallow_sqlalchemy import ModelSchema
from project.database import db

from project.modules.category.schema import CategorySchema

from .model import User
'''
class UserSchema(ModelSchema):
    class Meta:
        json_module = json
        strict = True
        sqla_session = db.session
        model = User
    
    self_url = ma.Url(attribute='selfApiUrl')'''

class UserSchema(ma.Schema):
    class Meta:
        json_module = json
        strict = True
        fields = (
            'id',
            'full_name',
            'registered_at',
            'last_visited_at',
            'phone',
            'email',
            'city',
            'active',
            'doer',
            'task_categories',
            'balance',
            'roles',
            'age',
            'about',
            'rating',
            'email_confirmed',
            'self_url'
        )
    
    self_url = ma.Url(attribute='selfApiUrl')
    balance = ma.Float()
    task_categories = ma.Nested(CategorySchema, only=('id', 'name', 'url_name', 'self_url'), many=True)
    #customer = ma.Nested(TaskStatusEnumSchema, exclude=('created_tasks',))
    #customer = db.Nested()

user_schema = UserSchema(exclude=('password', 'password_salt'))