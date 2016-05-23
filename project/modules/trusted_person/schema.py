from project.utils import json
from project.marshalling import ma

from project.modules.user.schema import UserSchema

class TrustedPersonSchema(ma.Schema):
    class Meta:
        json_module = json
        strict = True
        fields = (
            'id',
            'description',
            'full_name',
            'phone',
            'user'
        )
    
    self_url = ma.Url(attribute='selfApiUrl')
    user = ma.Nested(UserSchema, only=('id', 'full_name', 'age'))