import dateutil.parser
from flask import url_for, redirect
from flask.ext.login import login_required, current_user
from flask_restful import Resource, abort, reqparse, fields, marshal_with, marshal

from project.database import db

from project.util import api_login_required

from .schema import PrivateMessageSchema
from .model import PrivateMessage


class PrivateMessageAPI(Resource):

    @api_login_required
    def get(self, id):
        entity = PrivateMessage.query.get(id)
        if not entity:
            abort(404, message='No pm with id {}'.format(id))
        if entity.receiver.id != current_user.id:
            abort(403, message='Access denied')
        return PrivateMessageSchema().dump(entity).data

class PrivateMessageListAPI(Resource):

    @api_login_required
    def post(self):
       
        locs = ['values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('receiver_id', required=True, location=locs, type=int)
        parser.add_argument('text', required=True, location=locs)
        
        args = parser.parse_args()

        pm = PrivateMessage(sender_id=current_user.id, **args)
        try:
            db.session.add(pm)
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return redirect(url_for('api.pm', id=pm.id, _external=True), code=303)
    
    @api_login_required
    def get(self):
       # TODO
       pass