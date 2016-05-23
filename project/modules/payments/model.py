import datetime

from project.database import db, Model, Column, relationship
from project import config

class Payment(Model):
    id = Column(db.Integer, primary_key=True)
    
    user_id = Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', foreign_keys=[user_id], backref=db.backref('payments', lazy='dynamic'), uselist=False)

    done = Column(db.Boolean, default=False, nullable=False)
    
    created_at = Column(db.DateTime, default=datetime.datetime.utcnow)