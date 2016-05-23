from flask import url_for
from project.marshalling import ma
from project.database import db

from project.modules.user.schema import UserSchema

from .model import PrivateMessage

class PrivateMessageSchema(ma.Schema):
    class Meta:
        strict = True
        fields = (
            'id',
            'sender',
            'receiver',
            'created_at',
            'text',
            'self_url'
        )
    
    self_url = ma.Function(lambda pm: url_for('api.pm', id=pm.id, _external=True))
    sender = ma.Nested(UserSchema, only=('id', 'full_name', 'self_url'))
    receiver = ma.Nested(UserSchema, only=('id', 'full_name', 'self_url'))

private_message_schema = PrivateMessageSchema()