import datetime
from project.database import db, Model, Column, relationship

class TaskConfirmation(Model):
    id = Column(db.Integer, primary_key=True)

    created_at = Column(db.DateTime, default=datetime.datetime.utcnow)
    
    task_id = Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    task = relationship('Task', foreign_keys=[task_id], backref=db.backref('confirmations', lazy='dynamic'), uselist=False)

    sender_id = Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender = relationship('User', foreign_keys=[sender_id], backref=db.backref('task_confirmations', lazy='dynamic'), uselist=False)