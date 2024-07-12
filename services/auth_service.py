import datetime
from typing import Any
from flask import jsonify
from models.user import User
import jwt
import os


class Authentication:
    def __init__(self) -> None:
        super().__init__()

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)

    def __format__(self, format_spec: str) -> str:
        return super().__format__(format_spec)

    @staticmethod
    def login(matriculate: str, password: str):
        user = User.query.filter_by(matriculate=matriculate).first()
        if user and user.password == password:
            token = jwt.encode(
                {'user': user.to_dict(), 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                os.getenv('JWT_SECRET_KEY', 'default_secret_key'),
                algorithm='HS256'
            )
            return jsonify({'token': token, 'user': user.to_dict()}), 200
        else:
            return jsonify({'error': 'Invalid matriculate or password'}), 401
