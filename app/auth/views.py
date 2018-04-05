# coding=utf8


from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from app.decorators import admin_required, permission_required
from . import auth
from .forms import LoginForm, ChangePasswordForm, ResetPasswordForm, ResetPasswordRequestForm, ChangeEmailRequestForm
from .forms import RegistrationForm
from .. import db
from ..email import send_email
from ..models import User, Permission


@auth.route('/login', methods=['POST', 'GET'])
def login():
    # 如果不是匿名用户（已登录），则直接重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('main.hello'))
    # print "request.args.get('next') = ", request.args.get('next')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email_or_username.data).first() \
               or User.query.filter_by(username=form.email_or_username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # 由未授权的URL转到login来的话，Flask-Login会把之前的查询字符串的next 参数中
            # 之前的页面链接可通过request.args字典获取
            return redirect(request.args.get('next') or url_for('main.hello'))
        flash(u'账户或密码错误')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
# 如果未认证的用户访问这个路由，Flask-Login 会拦截请求，把用户发往登录页面
@login_required
def logout():
    # auth.session.pop('username', None)
    # auth.session.pop('email', None)
    logout_user()
    flash(u'你已经退出登录')
    return redirect(url_for('main.hello'))


@auth.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token(900)
        send_email(form.email.data, u'世界', 'auth/email/confirm', user=user, token=token)
        flash(u'注册成功，现在可以登陆啦')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


# login_required:保护路由，如果未登录会转到登录页面
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.hello'))
    if current_user.confirm(token):
        flash(u'你已经确认了你的帐号,谢谢!')
    else:
        flash(u'确认链接无效或已过期.')
    return redirect(url_for('main.hello'))


# 钩子函数，拦截请求。即使在蓝本之外
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
    # 用户已经登录、用户未激活、请求的端点（使用request.endpoint 获取）不在认证蓝本中
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


# 已经登录，但是没有激活的用户返回请求激活链接，未登录用户和已激活用户首页
@auth.route('/unconfirmed')
def unconfirmed():
    # current_user.is_anonymous:匿名用户返回True
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.hello'))
    return render_template('auth/unconfirmed.html')


# 重新发送激活邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, u'世界', 'auth/email/confirm', user=current_user, token=token)
    flash(u'一封新的确认邮件已经通过电子邮件发送给你.')
    return redirect(url_for('main.index'))


# 修改密码（已登录用户）
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash(u'密码已经修改成功.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


# 重置密码请求（无法登陆用户通过邮箱重置密码）
@auth.route('/reset', methods=['GET', 'POST'])
def reset_password_request():
    if not current_user.is_anonymous:
        redirect('main.hello')
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token(900)
            send_email(form.email.data, u'重置你的密码', 'auth/email/reset_password', user=user, token=token)
            flash(u'我们已发送一封邮件给你的邮箱，按照邮件提示重置你的密码')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


# 重置密码
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        redirect('main.hello')
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.hello'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailRequestForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, u'确认你的邮箱',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash(u'一封附有说明的确认你的新邮件地址的邮件已经发送给你')
            return redirect(url_for('main.hello'))
        else:
            flash(u'无效的邮件或密码.')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash(u'你的邮箱已更新.')
    else:
        flash(u'无效的请求.')
    return redirect(url_for('main.hello'))


@auth.route('/admin')
@login_required
@admin_required
def only_admin():
    return 'for admin'


@auth.route('/moderator')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    return "For comment moderators!"

















