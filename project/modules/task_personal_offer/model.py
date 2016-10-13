import datetime
from project.database import db, Model, Column, relationship

from project.modules.task.model import Task

class TaskPersonalOffer(Model):
    id = Column(db.Integer, primary_key=True)
    text = Column(db.Text, nullable=False)
    created_at = Column(db.DateTime, default=datetime.datetime.utcnow)
    
    task_id = Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    task = relationship('Task', foreign_keys=[task_id], uselist=False)

    sender_id = Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender = relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_personal_offers', lazy='dynamic'), uselist=False)
    
    receiver_id = Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver = relationship('User', foreign_keys=[receiver_id], backref=db.backref('received_personal_offers', lazy='dynamic'), uselist=False)