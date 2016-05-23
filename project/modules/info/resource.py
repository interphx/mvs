import dateutil.parser
from flask import url_for, redirect, render_template
from flask.ext.login import login_required, current_user
from flask_restful import Resource, abort, reqparse, fields, marshal_with, marshal

import project.utils
from project.utils import json
from project.database import db

from project.util import api_login_required, api_rights_required

from .model import InfoPage

class InfoPageListAPI(Resource):
    @api_rights_required('admin')
    def post():
        locs = ['values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True, location=locs)
        parser.add_argument('text', required=True, location=locs)
        
        args = parser.parse_args()

        page = InfoPage(**args)
       
        try:
            db.session.add(page)
            db.session.commit()
        except:
            db.session.rollback()
            raise 

class InfoPageAPI(Resource):  
    '''@api_rights_required('admin')
    def update(id):
        # TODO
        page = InfoPage.query.get(id)
        if not page:
            return '{message: "No such page id: ' + str(id) + '" }'
        try:
            page.delete()
            db.session.commit()
        except:
            db.session.rollback()
            raise'''

    @api_rights_required('admin')
    def delete(self, id):
        page = InfoPage.query.filter_by(id=id)
        if not page:
            return '{message: "No such page id: ' + str(id) + '" }'
        try:
            page.delete()
            db.session.commit()
        except:
            db.session.rollback()
            raise
        