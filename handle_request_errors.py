from functools import wraps
from flask import jsonify


def handle_errors(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    return decorated_function