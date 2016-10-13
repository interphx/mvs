import datetime
from flask.ext.login import UserMixin, AnonymousUserMixin
from sqlalchemy.orm import column_property
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func

from project.modules.user_role import role_to_user
from project.modules.user_rating import UserRating
from project.database import db, Model, Column, relationship
from project import config

category_to_doer = db.Table('category_to_doer',
    Column('category_id', db.Integer, db.ForeignKey('category.id')),
    Column('user_id', db.Integer, db.ForeignKey('user.id'))
)   

class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.full_name = 'anonymous'
        self.rights = 'guest'
        self.task_categories = dict()

class UloginData(Model):
    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = relationship('User', foreign_keys=[user_id], backref=db.backref('social_identities', lazy='dynamic'), uselist=False)
    network = Column(db.String(64), nullable=False)
    identity = Column(db.String(160), nullable=False)

class User(Model, UserMixin):
    id = Column(db.Integer, primary_key=True)
    full_name = Column(db.String(255), nullable=False)
    registered_at = Column(db.DateTime, default=datetime.datetime.utcnow)
    last_visited_at = Column(db.DateTime, default=None)

    phone = Column(db.String(100))
    email = Column(db.String(100), unique=False)
    
    #created_tasks = relationship('Task', backref='customer', lazy='dynamic')
    #assigned_tasks = relationship('Task', backref='doer', lazy='dynamic')
    
    password = Column(db.String(64), nullable=False)
    password_salt = Column(db.String(8), nullable=False)
    
    city = Column(db.String(255), nullable=False)
    
    active = Column(db.Boolean, default=True, nullable=False) # Is account activated
    email_confirmed = Column(db.Boolean, default=False, nullable=False) # Is account activated
    phone_confirmed = Column(db.Boolean, default=False, nullable=False) # Is phone confirmed
    doer = Column(db.Boolean, default=True, nullable=False)   # Does a user have doer rights
    
    task_categories = relationship('Category', secondary=category_to_doer, backref=db.backref('doers', lazy='dynamic'))
    
    balance = Column(db.Numeric(precision=15, scale=2), default=0)
    
    avatar_id = Column(db.Integer, db.ForeignKey('upload.id'), nullable=True)
    avatar = relationship('Upload', foreign_keys=[avatar_id], uselist=False)

    rights = Column(db.String(100), nullable=False, default='user')

    # deprecated
    roles = db.relationship('Role', secondary=role_to_user, backref=db.backref('users', lazy='dynamic'))
    
    age = Column(db.Integer)
    
    about = Column(db.Text(2048), default='')
    
    deleted = Column(db.Boolean, default=False, nullable=False)

    _rating = Column('rating', db.Float, nullable=False, default=0.0)
    
    def delete(self):
        self.deleted = True
        self.phone = '000000000'
        self.email = 'deleted_email@deleted.deleted'
        self.rights = 'deleted'
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

    @hybrid_property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        raise Exception('Please, use User.add_rating(rater, value) and User.remove_rating(rating_id) methods')

    def make_doer(self):
        self.doer = True
        if self.balance == None:
            self.balance = 0
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

    def unmake_doer(self):
        self.doer = False
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise


    def add_rating(self, rater, value):
        rating = UserRating(owner=self, rater=rater, value=value)
        try:
            db.session.add(rating)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        self._rating = db.session.query(func.avg(UserRating.value).label('average')).filter(UserRating.owner_id==self.id).one()[0] or 0

    def remove_rating(self, id):
        rating = UserRating.query.get(id)
        if rating == None:
            raise Exception('No user rating with id ' + str(id))

        try:
            db.session.delete(rating)
            db.session.commit()
        except:
            db.session.rollback()
            raise
        self._rating = db.session.query(func.avg(UserRating.value).label('average')).filter(UserRating.owner_id==self.id).one()[0] or 0

    def is_active(self):
        return self.active
    
    def is_anonymous(self):
        return False
    
    def is_authenticated(self):
        return True
    
    def get_id(self):
        return str(self.id)