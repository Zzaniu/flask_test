# coding=utf8


from flask import render_template
from . import main


# 定义404错误模板
@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# 定义500错误模板
@main.app_errorhandler(500)
def internal_sever_error(e):
    return render_template('500.html'), 500
