# coding=utf8


from flask import g, jsonify
from ..models import AnonymousUser, User
from flask_httpauth import HTTPBasicAuth
from .errors import unauthorized, forbidden
from . import api

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_username_or_token, password):
    if email_or_username_or_token == '':
        # g:程序上下文，处理请求时用作临时存储的对象。每次请求都会重设这个变量
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_username_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_username_or_token).first() or\
        User.query.filter_by(username=email_or_username_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@api.route('/token')
def get_token():
    if g.current_user.is_anonymous() or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
                    expiration=900), 'expiration': 900})


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


# 作用域只在该蓝本之内，使用auth.login_required保护该蓝本中所有的路由
@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')



























