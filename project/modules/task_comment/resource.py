import dateutil.parser
from flask import url_for, redirect
from flask.ext.login import login_required, current_user
from flask_restful import Resource, abort, reqparse, fields, marshal_with, marshal

import project.utils
from project.utils import json
from project.database import db

from project.util import api_login_required

from .schema import TaskCommentSchema

from .model import TaskComment

class TaskCommentAPI(Resource):

    def get(self, id):
        entity = TaskComment.query.get(id)
        if not entity:
            abort(404, message='No task comment with id {}'.format(id))
        return TaskCommentSchema().dump(entity).data

class TaskCommentListAPI(Resource):

    @api_login_required
    def post(self):
       
        locs = ['values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('task_id', required=True, location=locs, type=int)
        parser.add_argument('text', required=True, location=locs)
        
        args = parser.parse_args()

        comment = TaskComment(author_id=current_user.id, **args)
        try:
            db.session.add(comment)
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return redirect(url_for('api.task_comment', id=comment.id, _external=True), code=303)
    
    @api_login_required
    def get(self):
       # TODO
       pass