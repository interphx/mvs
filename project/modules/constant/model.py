import json
import itertools
from flask import url_for
from project.database import db, Model, Column, relationship, TextPickleType
from project.util import urlify

class CommissionSettings(Model):
	id = Column(db.Integer, primary_key=True)
	lower_bound = Column(db.Integer, nullable=False)
	upper_bound = Column(db.Integer, nullable=False)
	commission = Column(db.Float, default=0.1, nullable=False)

class Constant(Model):
    id = Column(db.Integer, primary_key=True)
    slogan = Column(db.Text, default='', nullable=False)
    min_commission = Column(db.Integer, default=100, nullable=False)
    active = Column(db.Boolean, default=True)
    seo_keywords = Column(db.Text, default='')
    seo_description = Column(db.Text, default='')