# coding=utf8


from flask import render_template, session, redirect, url_for, flash

from . import main
from .forms import NameForm
from .. import db
from ..models import User, Role
from ..email import send_email


@main.route('/index', methods=['GET', 'POST'])
def index():
    form = NameForm()
    name = form.name.data
    email = form.email.data
    password = form.password.data
    # print "form.users.data = ", form.users.data
    # print "form.validate_on_submit() is : ", form.validate_on_submit()
    # print "form.errors = ", form.errors
    # print "form.data = ", form.data
    if form.validate_on_submit():
        # if form.data['submit']:
        old_name = session.get('name')
        user = User.query.filter_by(username=form.name.data).first()
        role = Role.query.all()
        # print 'role = ', role
        if user is None:
            user = User(username=name, age=form.age.data, \
                        email=email, role=role[int(form.users.data)])
            user.password = password
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            send_email(email, u'Email', 'main/email/hello_user', user=user, fujian=True)
        else:
            session['known'] = True
        if old_name is not None and old_name != form.name.data:
            flash(u'Hello %s, 你改变了你的名字,原名字: %s' % (form.name.data, old_name))
        session['name'] = form.name.data
        return redirect(url_for('.index'))
    return render_template('index.html', form=form, name=session.get('name'),\
                           known=session.get('known', False))


@main.route('/')
def hello():
    return render_template('hello.html')
