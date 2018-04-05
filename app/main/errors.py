# coding=utf8


from flask import render_template, request, jsonify
from . import main


# 定义404错误模板
@main.app_errorhandler(404)
def page_not_found(e):
    # 为Json格式的客户端生成Json响应（REST API 响应一般都是JSON）
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


# 定义500错误模板
@main.app_errorhandler(500)
def internal_sever_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('500.html'), 500


@main.app_errorhandler(403)
def blocking_access(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('403.html'), 403

