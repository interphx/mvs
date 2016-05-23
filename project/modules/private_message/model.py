import datetime

from project.database import db, Model, Column, relationship
from project import config

class PrivateMessage(Model):
    id = Column(db.Integer, primary_key=True)
    text = Column(db.Text(), nullable=False)
    
    sender_id = Column(db.Integer, db.ForeignKey('user.id'))
    sender = relationship('User', foreign_keys=[sender_id], backref=db.backref('pms_sent', lazy='dynamic'), uselist=False)    
    
    receiver_id = Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver = relationship('User', foreign_keys=[receiver_id], backref=db.backref('pms_received', lazy='dynamic'), uselist=False)
    
    created_at = Column(db.DateTime, default=datetime.datetime.utcnow)