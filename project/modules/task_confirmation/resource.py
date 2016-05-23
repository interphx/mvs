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
from project.modules.user_comment.model import UserComment

from .model import TaskConfirmation

class TaskConfirmationListAPI(Resource):

    @api_login_required
    def post(self):
        locs = ['values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('task_id', required=True, location=locs, type=int)
        parser.add_argument('text', required=True, location=locs)
        parser.add_argument('rating', required=True, location=locs, type=int)
        
        args = parser.parse_args()

        task = Task.query.get(args['task_id'])
        if task == None:
            abort(400, message='No task with id {}'.format(args['task_id']))
        if task.doer == None:
            abort(400, message='No doer is assigned to this task yet')

        rating = int(args['rating'])
        if not (1 <= rating <= 5):
            abort(400, message='Rating must be between 1 and 5 inclusive')

        customer = task.customer
        doer = task.doer

        # TODO: проверить
        if task.confirmations.filter_by(sender_id=current_user.id).count() > 0:
            abort(403, message='You cannot confirm task execution more than once')

        if current_user.id == customer.id:
            # Отзыв об исполнителе
            comment = UserComment(task_id=task.id, author_id=current_user.id, owner_id=doer.id, text=args['text'])
            doer.add_rating(customer, rating)
        elif current_user.id == task.doer.id:
            # Отзыв о заказчике
            comment = UserComment(task_id=task.id, author_id=current_user.id, owner_id=customer.id, text=args['text'])
            customer.add_rating(doer, rating)
        else:
            abort(403, message='You cannot confirm execution of others\' tasks')

        if task.confirmations.count() == 1:
            task.status = Task.Status.completed

        confirmation = TaskConfirmation(sender_id=current_user.id, task_id=task.id)

        try:
            db.session.add(confirmation)
            db.session.add(comment)
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return {}, 200
    
    @api_login_required
    def get(self):
       # TODO
       pass