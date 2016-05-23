import datetime
from project.database import db, Model, Column, relationship
from project.util import urlify

class InfoPage(Model):
    id = Column(db.Integer, primary_key=True)
    url_name = Column(db.String(255), unique=True, default=lambda context: urlify(context.current_parameters['title']))
    text = Column(db.Text, nullable=False)
    title = Column(db.Text(4096), nullable=False)
    listed = Column(db.Boolean, default=True)
    sort_order = Column(db.Integer, default=1, nullable=False)