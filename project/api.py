from flask import Blueprint, jsonify

api = Blueprint('api/v1', __name__)

@api.route('/')
def index():
    return jsonify(**{
        'categories': '/cats'
    })