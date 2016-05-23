from flask import url_for

from project.utils import json
from project.marshalling import ma

class CategorySchema(ma.Schema):
    
    class Meta:
        json_module = json
        strict = True
        fields = (
            'id',
            'name',
            'url_name',
            'tasks_url',
            'self_url',
            'children'
        )
    
    tasks_url = ma.Function(lambda cat: url_for('api.category_tasks', url_name=cat.url_name, _external=True))
    self_url = ma.Url(attribute='selfApiUrl')
    children = ma.Nested('self', only=('id', 'name', 'url_name', 'self_url', 'tasks_url'), many=True)

class CategoryListSchema(ma.Schema):
    
    class Meta:
        json_module = json
        strict = True
    