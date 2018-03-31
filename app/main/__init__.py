# coding=utf8


from flask import Blueprint

# 实例化一个Blueprint类对象创建蓝本
main = Blueprint('main', __name__)

from . import views, errors