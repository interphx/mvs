import datetime
from project.database import db, Model, Column, relationship

class TrustedPerson(Model):
    id = Column(db.Integer, primary_key=True)
    full_name = Column(db.Text(512), nullable=False)
    description = Column(db.Text, nullable=False)
    phone = Column(db.String(64), nullable=False)
    
    user_id = Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = relationship('User', foreign_keys=[user_id], backref=db.backref('trusted_persons', lazy='dynamic'), uselist=False)
    