from flask import jsonify, request, g, url_for, current_app
from .. import db
from . import api


@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    return jsonify({
        'posts': 212,
        'count': page
    })
