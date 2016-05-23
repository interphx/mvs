import dateutil.parser
from flask import url_for, redirect, render_template
from flask.ext.login import login_required, current_user
from flask_restful import Resource, abort, reqparse, fields, marshal_with, marshal

import project.utils
from project.utils import json
from project.database import db

from project.util import api_login_required, get_commission

from .model import *
from .schema import *

class TrustedPersonListAPI(Resource):

    @api_login_required
    def post(self):
        locs = ['values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('full_name', required=True, location=locs, type=str)
        parser.add_argument('description', required=True, location=locs, type=str)
        parser.add_argument('phone', required=True, location=locs, type=str)
        
        args = parser.parse_args()

        person = TrustedPerson(
            full_name = args['full_name'],
            description = args['description'],
            phone = args['phone'],
            user_id = current_user.id
        )
        
        try:
            db.session.add(person)
            db.session.commit()
        except Exception as e:
            abort(400, message='Ошибка базы данных: ' + str(e))
            db.session.rollback()

        return TrustedPersonSchema().dump(person).data

class TrustedPersonAPI(Resource):

    def get(self, id):
        entity = TrustedPerson.query.get(id)
        if not entity:
            abort(404, message='No trusted person with id {}'.format(id))
        return TrustedPersonSchema().dump(entity).data

    def delete(self, id):
        entity = TrustedPerson.query.get(id)
        if not entity:
            abort(404, message='No trusted person with id {}'.format(id))
        try:
            db.session.delete(entity)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        return {}, 204