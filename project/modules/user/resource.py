import dateutil.parser
from flask import url_for, redirect
from flask_restful import Resource, abort, reqparse
from flask.ext.login import current_user

import project.utils
from project.util import normalize_mobile
from project.utils import json
from project.database import db

from project.modules.category.model import Category

from .schema import user_schema

from .model import User
from .helpers import check_password, set_user_password

class UserPasswordChangeAPI(Resource):
    def post(self, id):
        user = User.query.get(id)
        if not user:
            abort(404, message='No user with id {}'.format(id))
        if not current_user.is_authenticated or current_user.id != user.id:
            abort(403, message='У вас нет прав для совершения этого действия')
        
        locs = ['values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('password_old', required=True, location=locs, type=str)
        parser.add_argument('password_new', required=True, location=locs, type=str)
        
        args = parser.parse_args()
        
        if not check_password(user, args['password_old']):
            abort(400, message='Введённый старый пароль не совпадает с существующим')
        
        set_user_password(user, args['password_new'])
        return redirect(url_for('api.user', id=user.id, _external=True), code=303)        

class UserAPI(Resource):

    def get(self, id):
        result = User.query.get(id)
        if not result:
            abort(404, message='No user with id {}'.format(id))
        return user_schema.dump(result).data
    
    def delete(self, id):
        user = User.query.filter_by(id=id).first()
        if not user:
            abort(404)
        if  (not current_user.is_authenticated or not current_user.id == id) and current_user.rights != 'admin':
            abort(403, message='У вас нет прав для совершения этого действия')
        user.delete()
        

    def put(self, id):
        if not current_user.is_authenticated:
            abort(403, message='У вас нет прав для совершения этого действия')

        locs = ['values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('full_name', required=False, location=locs)
        parser.add_argument('about', required=False, location=locs)
        parser.add_argument('phone', required=False, location=locs)
        parser.add_argument('age', required=False, location=locs)
        parser.add_argument('balance', required=False, location=locs)
        parser.add_argument('task_categories', required=False, location='json', type=list)

        # Remove None-items
        args = {k: v for k, v in parser.parse_args().items() if v is not None}
        if 'phone' in args:
            args['phone'] = normalize_mobile(args['phone'])

        user_query = User.query.filter_by(id=int(current_user.id))
        user = user_query.one()

        if 'task_categories' in args:
            args['task_categories'] = [Category.query.get(int(cat_id)) for cat_id in args['task_categories']]
            user.task_categories = args['task_categories']
            args.pop('task_categories')
        
        if 'balance' in args:
            if not current_user.rights == 'admin':
                abort(403, message='У вас нет прав для совершения этого действия')
        
        try:
            if len(args) > 0:
                user_query.update(args)
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return redirect(url_for('api.user', id=current_user.id, _external=True), code=303)

class UserListAPI(Resource):
    def post(self):
        # TODO
        print(current_user)
        locs = ['values', 'json']
        
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True, location=locs)
        parser.add_argument('category_id', required=True, location=locs, type=int)
        parser.add_argument('customer_id', required=True, location=locs, type=int)
        parser.add_argument('description', required=True, location=locs)
        parser.add_argument('due', required=True, location=locs, type=lambda x: dateutil.parser.parse(x))
        parser.add_argument('addresses', required=True, location=locs, action='append')
        parser.add_argument('reward', location=locs, type=float, default=None)
        parser.add_argument('contacts', required=True, location=locs, type=dict, action='append')
        
        args = parser.parse_args()

        task = Task(**args)
        try:
            db.session.add(task)
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return redirect(url_for('api.task', id=task.id, _external=True), code=303)