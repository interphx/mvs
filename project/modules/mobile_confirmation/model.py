import datetime

from project.database import db, Model, Column, relationship
from project import config

class MobileConfirmation(Model):
    id = Column(db.Integer, primary_key=True)
    code = Column(db.String(32), nullable=False)
    
    user_id = Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', foreign_keys=[user_id], uselist=False)
    
    created_at = Column(db.DateTime, default=datetime.datetime.utcnow)