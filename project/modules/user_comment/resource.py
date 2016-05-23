import dateutil.parser
from flask import url_for, redirect, render_template
from flask.ext.login import login_required, current_user
from flask_restful import Resource, abort, reqparse, fields, marshal_with, marshal

import project.utils
from project.utils import json
from project.database import db

from project.util import api_login_required

from project.modules.user.helpers import notify_user
from project.modules.task.model import Task
from project.modules.user.model import User

from .model import UserComment

class UserCommentListAPI(Resource):

    @api_login_required
    def post(self):
        locs = ['values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('task_id', required=True, location=locs, type=int)
        parser.add_argument('user_id', required=True, location=locs, type=int)
        parser.add_argument('text', required=True, location=locs)
        
        args = parser.parse_args()

        task = Task.query.get(args['task_id'])
        if task == None:
            abort(404, 'No task with id {}'.format(args['task_id']))
        if task.doer == None:
            abort(400, 'No doer is assigned to this task yet')

        user = User.query.get(args['user_id'])
        if user == None:
            abort(404, 'No user with id {}'.format(args['user_id']))

        comment = UserComment()

        # TODO: проверить
        if task.confirmations.filter_by(sender_id=current_user.id).count() > 0:
            abort(403, 'You cannot confirm task execution more than once')

        if current_user.id == customer.id:
            # Отзыв об исполнителе
            # TODO: create user_review
            doer.add_rating(customer, rating)
        elif current_user.id == task.doer.id:
            # Отзыв о заказчике
            # TODO: create user_review
            customer.add_rating(doer, rating)
        else:
            abort(403, 'You cannot confirm execution of others\' tasks')

        if task.confirmations.count() == 2:
            task.status = Task.Status.completed

        confirmation = TaskConfirmation(sender_id=current_user.id, task_id=task.id)

        try:
            db.session.add(confirmation)
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return {}, 200
    
    @api_login_required
    def get(self):
       # TODO
       pass