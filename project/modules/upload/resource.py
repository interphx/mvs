import dateutil.parser
import werkzeug
from flask import url_for, redirect, render_template
from flask.ext.login import login_required, current_user
from flask_restful import Resource, abort, reqparse, fields, marshal_with, marshal

import project.utils
from project.utils import json
from project.database import db

from project.util import api_login_required


from .model import Upload
from .helpers import upload_file

class WysiwygUploadAPI(Resource):
    @api_login_required
    def post(self):
        locs = ['files']
        parser = reqparse.RequestParser()
        parser.add_argument('fileToUpload', required=True, location=locs, type=werkzeug.FileStorage)
        args = parser.parse_args()
        file = upload_file(args['fileToUpload'], description='Изображение для страницы сайта', role='other', author_id=None)
        
        return {'file': file.url, 'success': True}

class UploadListAPI(Resource):

    @api_login_required
    def post(self):
        locs = ['files', 'values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('role', required=True, location=locs, type=str)
        parser.add_argument('type', required=True, location=locs, type=str)
        parser.add_argument('description', required=False, location=locs, type=str, default="")
        parser.add_argument('file', required=True, location=locs, type=werkzeug.FileStorage)
        
        args = parser.parse_args()
        file = upload_file(args['file'], description=args['description'], role='portfolio', author_id=current_user.id)
        
        return {'file': file.url, 'success': True}
    
    @api_login_required
    def get(self):
       # TODO
       pass