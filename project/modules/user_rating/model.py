from project.database import Model, db, Column, relationship

class UserRating(Model):
    id = Column(db.Integer, primary_key=True)
    value = Column(db.Float)
    
    owner_id = Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = relationship('User', foreign_keys=[owner_id], backref=db.backref('ratings_received', lazy='dynamic'), uselist=False)
    
    rater_id = Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rater = relationship('User', foreign_keys=[rater_id], backref=db.backref('ratings_delivered', lazy='dynamic'), uselist=False)