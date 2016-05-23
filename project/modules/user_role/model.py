import datetime
from project.database import db, Model, Column, relationship

role_to_user = db.Table('role_to_user',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(Model):
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(255), nullable=False, unique=True)