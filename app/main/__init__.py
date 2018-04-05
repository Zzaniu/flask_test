# coding=utf8


from flask import Blueprint

# 实例化一个Blueprint类对象创建蓝本
main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission


# 使用上下文处理器。上下文处理器能让变量在所有模板中全局可访问
# Permission可在所有模板中当做一个全局变量
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
