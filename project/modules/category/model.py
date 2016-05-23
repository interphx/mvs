import json
import itertools
from flask import url_for
from project.database import db, Model, Column, relationship, TextPickleType
from project.util import urlify

# Also has field tasks (defined in modules/task/model.py)
class Category(Model):
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(255))
    url_name = Column(db.String(255), unique=True, default=lambda context: urlify(context.current_parameters['name']))
    parent_id = Column(db.Integer, db.ForeignKey('category.id'), default=None)
    parent = relationship('Category', remote_side=[id], backref=db.backref('children', lazy='dynamic'))
    additional_fields = Column(TextPickleType(), default='', nullable=False)
    
    @property
    def selfApiUrl(self):
        return url_for('api.{}'.format(self.__table__.name), url_name=self.url_name, _external=True)

    # Returns self id and all descendants' ids in a list
    def getTreeIds(self):
        return list(itertools.chain([self.id], *[child.getTreeIds() for child in self.children]))

    @property
    def tasks_query(self):
        return self.get_tasks(just_query=True)

    def get_tasks(self, just_query=False):
        from project.modules.task import Task
        cat_ids = self.getTreeIds()
        query = Task.query.filter(Task.category_id.in_(cat_ids))

        if just_query:
            return query
        return query.all()

    @property
    def doers_query(self):
        return self.get_doers(just_query=True)

    def get_doers(self, just_query=False):
        from project.modules.user import User
        cat_ids = self.getTreeIds()
        query = User.query.filter(User.task_categories.any(Category.id.in_(cat_ids)))

        if just_query:
            return query
        return query.all()

    @property
    def isSubCategory(self):
        return self.parent and self.parent.url_name != 'all'

    @property
    def isSuperCategory(self):
        return self.url_name == 'all' or self.parent == None
    