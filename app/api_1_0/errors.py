# coding=utf8


from flask import jsonify
from app.exceptions import ValidationError
from . import api


# 坏请求-请求不可用或不一致
def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


# 未授权-请求未包含认证信息
def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


# 禁止-请求中发送的认证密令无权访问目标
def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
