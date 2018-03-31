# coding=utf8


from flask import current_app, render_template
from flask_mail import Message, Mail
from threading import Thread
from . import mail
import os


def send_async_email(app, msg):
    # send函数使用current_app，要在激活的程序上下文中执行
    with app.app_context():
        mail.send(msg)


def send_email(email, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(subject='Flask-' + subject,\
                  # sender=os.environ.get('MAIL_USERNAME'),\
                  recipients=[email])
    # msg.body = 'Send By Flask-Email'
    # msg.html = u'<b>Send By Flask-Email</b>'
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    if kwargs.get('fujian', False):
        with app.open_resource("static/p1.gif") as fp:
            msg.attach("p1.gif", "p1/gif", fp.read())
        with app.open_resource("static/p2.mp4") as fp:
            msg.attach("p2.mp4", "p2/mp4", fp.read())
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()
