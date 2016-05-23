import datetime
from project.database import db, Model, Column, relationship, TextPickleType
from project.util import urlify

class Task(Model):

    class Status:
        created = 'created'
        assigned = 'assigned'
        completed = 'completed'

    id = Column(db.Integer, primary_key=True)
    title = Column(db.String(255), nullable=False)
    description = Column(db.Text, nullable=False)
    created_at = Column(db.DateTime, default=datetime.datetime.utcnow)
    due = Column(db.DateTime, nullable=False)
    
    customer_id = Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer = relationship('User', foreign_keys=[customer_id], backref=db.backref('created_tasks', lazy='dynamic'), uselist=False)
    
    category_id = Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = relationship('Category', backref=db.backref('tasks', lazy='dynamic'), uselist=False)
    
    contacts = Column(TextPickleType(), nullable=False)
    
    status = Column(db.String(64), nullable=False, default='created')
    
    addresses = Column(TextPickleType(), nullable=False)
    
    # None means "let the doer decide"
    reward = Column(db.Numeric(precision=15, scale=2), default=None)
    
    doer_id = Column(db.Integer, db.ForeignKey('user.id'))
    doer = relationship('User', foreign_keys=[doer_id], backref=db.backref('assigned_tasks', lazy='dynamic'), uselist=False)
    
    additional_data = Column(TextPickleType(), default='', nullable=False)