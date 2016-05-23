import datetime

from project.database import db, Model, Column, relationship
from project import config

class DoerApplication(Model):
    id = Column(db.Integer, primary_key=True)
    
    user_id = Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', foreign_keys=[user_id], uselist=False)

    passport_scan_id = Column(db.Integer, db.ForeignKey('upload.id'), nullable=False)
    passport_scan = relationship('Upload', foreign_keys=[passport_scan_id], uselist=False)
    
    created_at = Column(db.DateTime, default=datetime.datetime.utcnow)