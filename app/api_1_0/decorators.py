# coding=utf8


from flask import g
from .errors import forbidden
from functools import wraps


# 防止未授权用户创建新博客文章
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
