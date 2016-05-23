from project.database import db, Model, Column, relationship
from project import config

class UserContact(Model):
    id = Column(db.Integer, primary_key=True)
    type = Column(db.String(64), nullable=False)
    value = Column(db.String(255), nullable=False)
    owner_id = Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = relationship('User', backref=db.backref('contacts', lazy='dynamic'), uselist=False)