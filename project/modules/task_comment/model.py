import datetime
from project.database import db, Model, Column, relationship

class TaskComment(Model):
    id = Column(db.Integer, primary_key=True)
    text = Column(db.Text, nullable=False)
    created_at = Column(db.DateTime, default=datetime.datetime.utcnow)
    
    task_id = Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    task = relationship('Task', foreign_keys=[task_id], backref=db.backref('comments', lazy='dynamic'), uselist=False)

    
    author_id = Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = relationship('User', foreign_keys=[author_id], backref=db.backref('comments', lazy='dynamic'), uselist=False)
    