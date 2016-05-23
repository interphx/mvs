from flask_restful import Api
from project import app

rest = Api(app, prefix='/api/v1')