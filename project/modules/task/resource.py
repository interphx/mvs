import datetime
import dateutil.parser
from flask import url_for, redirect
from flask.ext.login import login_required, current_user
from flask_restful import Resource, abort, reqparse, fields, marshal_with, marshal

import project.utils
from project.utils import json
from project.database import db

from project.util import api_login_required

from project.modules.user.model import User

from .schema import TaskSchema, TaskListSchema

from .model import Task

task_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'created_at': fields.DateTime,
    'due': fields.DateTime,
    'customer_id': fields.Raw,
    'category_id': fields.Raw,
    'contacts': fields.String,
    'status_id': fields.Raw,
    'addresses': fields.String,
    'reward': fields.Arbitrary,
    'doer_id': fields.Raw,
    'additional_data': fields.String
}

class TaskAPI(Resource):

    def get(self, id):
        entity = Task.query.get(id)
        if not entity:
            abort(404, message='No task with id {}'.format(id))
        return TaskSchema().dump(entity).data
    
    @api_login_required
    def delete(self, id):
        entity = Task.query.get(id)
        if not entity:
            abort(404, message='No task with id {}'.format(id))

        if entity.customer_id != current_user.id:
            abort(403, message='You cannot delete others\' tasks')

        try:
            db.session.delete(entity)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        return '', 200

    @api_login_required
    def put(self, id):
        entity = Task.query.get(id)
        if not entity:
            abort(404, message='No task with id {}'.format(id))

        if entity.customer_id != current_user.id:
            abort(403, message='You cannot edit others\' tasks')
        
        locs = ['values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True, location=locs)
        parser.add_argument('category_id', required=False, location=locs, type=int)
        parser.add_argument('description', required=False, location=locs)
        parser.add_argument('due', required=False, location=locs, type=lambda x: dateutil.parser.parse(x, dayfirst=True))
        parser.add_argument('addresses', required=False, location=locs, action='append')
        parser.add_argument('reward', required=False, location=locs, type=int, default=None)
        parser.add_argument('contacts', required=False, location=locs, type=dict, action='append')
        
        # Remove None-items
        args = {k: v for k, v in parser.parse_args().items() if v is not None}
        
        try:
            Task.query.filter_by(id=entity.id).update(args)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        return redirect(url_for('api.task', id=entity.id, _external=True), code=303)

class TaskListAPI(Resource):

    @api_login_required
    def post(self):
       
        locs = ['values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True, location=locs)
        parser.add_argument('category_id', required=True, location=locs, type=int)
        parser.add_argument('description', required=True, location=locs)
        parser.add_argument('due', required=True, location=locs, type=lambda x: dateutil.parser.parse(x, dayfirst=True))
        parser.add_argument('addresses', required=True, location=locs, action='append')
        parser.add_argument('reward', required=True, location=locs, type=int, default=None)
        parser.add_argument('contacts', required=True, location=locs, type=dict, action='append')
        
        args = parser.parse_args()

        task = Task(customer_id=current_user.id, **args)
        try:
            db.session.add(task)
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return redirect(url_for('api.task', id=task.id, _external=True), code=303)
    
    @api_login_required
    def get(self):
       # TODO
       pass

class UserTaskListAPI(Resource):
    def get(self, user_id):
        # TODO: Rename to clarify that this returns only unassigned tasks
        tasks = User.query.get(user_id).created_tasks.filter_by(status='created').filter(Task.due >= datetime.datetime.now()).order_by(Task.created_at.desc())
        return TaskListSchema().dump({'tasks': tasks}).data