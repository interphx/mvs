import datetime
from project.database import db, Model, Column, relationship

from project.modules.task.model import Task

def get_price_from_task(context):
	return Task.query.get(context.current_parameters['task_id']).reward

class TaskOffer(Model):
    id = Column(db.Integer, primary_key=True)
    text = Column(db.Text, nullable=False)
    created_at = Column(db.DateTime, default=datetime.datetime.utcnow)
    price = Column(db.Numeric(precision=15, scale=2), default=get_price_from_task)
    
    task_id = Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    task = relationship('Task', foreign_keys=[task_id], backref=db.backref('offers', lazy='dynamic'), uselist=False)

    doer_id = Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doer = relationship('User', foreign_keys=[doer_id], backref=db.backref('created_task_offers', lazy='dynamic'), uselist=False)
    