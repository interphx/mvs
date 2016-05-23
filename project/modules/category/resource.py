from flask import url_for
from flask_restful import Resource, abort, reqparse
from project.database import db
from .model import Category
from .schema import *
from .schema_tasks import *

class CategoryAPI(Resource):

    # TODO: Use flask-restful marshalling instead
    # TODO: Make API conform to standards
    def get(self, url_name):
        cat = Category.query.filter_by(url_name=url_name).first()
        if not cat:
            abort(404, message='No category with url_name {}'.format(id))
        result = CategorySchema().dump(cat).data
        result['self_url'] = url_for('api.category', _external=True, url_name = url_name)
        result['tasks_url'] = url_for('api.category_tasks', _external=True, url_name = url_name)
        return result

class CategoryTasksAPI(Resource):
    # TODO: Pagination
    def get(self, url_name):
        cat = Category.query.filter_by(url_name=url_name).first()
        if not cat:
            abort(404, message='No category with url_name {}'.format(url_name))
        result = CategoryTasksSchema().dump({
            'items': cat.tasks,
            'category_url': url_for('api.category', _external=True, url_name = url_name),
            'self_url': url_for('api.category_tasks', _external=True, url_name = url_name)
        }).data
        return result

class CategoryListAPI(Resource):
    # TODO: Use flask-restful marshalling instead
    # TODO: Make API conform to standards
    def post(self):
        locs = ['form', 'args', 'json']
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, location=locs)
        parser.add_argument('url_name', location=locs)
        parser.add_argument('parent_id', type=int, location=locs)
        parser.add_argument('additional_fields', location=locs)
    
        args = parser.parse_args()

        category = Category(**args)
        try:
            db.session.add(category)
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return category.asDict()