import datetime
from project.database import db, Model, Column, relationship

class Upload(Model):
    id = Column(db.Integer, primary_key=True)

    created_at = Column(db.DateTime, default=datetime.datetime.utcnow)

    author_id = Column(db.Integer, db.ForeignKey('user.id'))
    author = relationship('User', foreign_keys=[author_id], backref=db.backref('uploads', lazy='dynamic'), uselist=False)

    type = Column(db.String(64), nullable=False)
    role = Column(db.String(64), nullable=False)
    hash = Column(db.String(64), nullable=False)

    description = Column(db.String(512), nullable=False)

    mime = Column(db.String(255), nullable=False)

    file_path = Column(db.String(1024), nullable=False)
    url = Column(db.String(1024), nullable=False)