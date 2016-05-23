import pickle
import project.utils as utils
from sqlalchemy.orm import relationship
from sqlalchemy.inspection import inspect
from flask import url_for
from project import db

Column = db.Column

class TextPickleType(db.PickleType):
    impl = db.Unicode
    
    def __init__(self, protocol=pickle.HIGHEST_PROTOCOL, pickler=utils.json, comparator=None):
        super().__init__(protocol=protocol, pickler=pickler, comparator=comparator)

class Model(db.Model):
    """Base model class"""
    __abstract__ = True
    
    def asDict(self):
        """Represents entity as dictionary. Supports only columns that exist in DB"""
        return {field.name: getattr(self, field.name) for field in self.__table__.columns}
    
    @property
    def selfApiUrl(self):
        return url_for('api.{}'.format(self.__table__.name), id=self.id, _external=True)
    
    '''def __repr__(self):
        """Unique string representation of an entity"""
        cls = type(self)
        unique = ','.join([key.name + '=' + getattr(self, key.name) for key in cls.__table__.columns.keys()])
        return '{0}({1})'.format(cls.__name__, unique)'''