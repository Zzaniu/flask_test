# coding=utf8


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, RadioField, PasswordField, BooleanField, SelectField
from wtforms.validators import NumberRange, DataRequired, Email, EqualTo, Length, Regexp
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email_or_username = StringField(u'用户名或邮箱', validators=[
        DataRequired(message=u'请输入一个有效的用户名或邮箱！'),
        Length(1, 64),
    ])
    password = PasswordField(u'请确认你的密码', validators=[
        DataRequired(message=u'请输入一个有效数字！'),
        Length(8, 30, message=u'密码限制在8-30字符之间')
    ])
    remember_me = BooleanField(u'记住我')
    submit = SubmitField(u'登陆')


class RegistrationForm(FlaskForm):
    username = StringField(u'用户名', validators=[
        # 如果没有输入数据，则弹出message
        DataRequired(message=u'请输入用户名！'),
        # 如果输入数据长度不在范围内，则弹出message
        Length(3, 30, message=u'用户名限制在6-12字符之间'),
        Regexp(ur'^[A-Za-z0-9_\u4e00-\u9fa5]+$', 0,
               message=u'用户名必须只有汉字,字母，数字下划线')
    ])
    password = PasswordField(u'请设置你的密码', validators=[
        DataRequired(message=u'请输入一个有效数字！'),
        Length(8, 30, message=u'密码限制在8-30字符之间'),
        # 如果password2输入跟password不一致，则弹出message
        EqualTo('password2', message=u'两次输入的密码必须一致')
    ])
    password2 = PasswordField(u'请确认你的密码', validators=[
        DataRequired(message=u'请输入一个有效数字！'),
        Length(8, 30, message=u'密码限制在8-30字符之间')
    ])
    # age = IntegerField(u'你的年龄？', validators=[
    #     DataRequired(message=u'请输入一个有效数字！'),
    #     # 如果输入数字不在范围内，则弹出message
    #     NumberRange(18, 100, u'请输入18~100以内的数字！')])
    # choices中的元组里面的值可以为字符串，不能为数字，否则form.validate_on_submit()一直未false
    # 且form.errors中报错Not a valid choice
    # users = RadioField(u'用户组', choices=[
    #     ('0', 'admin'), ('1', 'User')], default='0')
    # language = SelectField(u'Programming Language', choices=[('cpp', 'C++'), ('py', 'Python'),\
    #                                  ('text', 'Plain Text')])
    email = StringField(u'请输入邮箱', validators=[
        # 如果输入数据不是一个有效的邮箱，则弹出message
        Email(message=u'您输入的邮箱有误')])
    submit = SubmitField(u'注册')

    # 如果表单类中定义了以validate_ 开头且后面跟着字段名的方法，这个方法就和常规的验证函数一起调用
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'该邮箱已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已存在')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'请输入当前密码', validators=[
        DataRequired(message=u'请输入一个有效数字！'),
        Length(8, 30, message=u'密码限制在8-30字符之间'),
    ])
    password = PasswordField(u'请设置你的密码', validators=[
        DataRequired(message=u'请输入一个有效数字！'),
        Length(8, 30, message=u'密码限制在8-30字符之间'),
        # 如果password2输入跟password不一致，则弹出message
        EqualTo('password2', message=u'两次输入的密码必须一致')
    ])
    password2 = PasswordField(u'请确认你的密码', validators=[
        DataRequired(message=u'请输入一个有效数字！'),
        Length(8, 30, message=u'密码限制在8-30字符之间')
    ])
    submit = SubmitField(u'修改密码')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(u'请输入邮箱', validators=[
        # 如果输入数据不是一个有效的邮箱，则弹出message
        Email(message=u'您输入的邮箱有误')])
    submit = SubmitField(u'重置密码')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(u'请设置你的密码', validators=[
        DataRequired(message=u'请输入一个有效数字！'),
        Length(8, 30, message=u'密码限制在8-30字符之间'),
        # 如果password2输入跟password不一致，则弹出message
        EqualTo('password2', message=u'两次输入的密码必须一致')
    ])
    password2 = PasswordField(u'请确认你的密码', validators=[
        DataRequired(message=u'请输入一个有效数字！'),
        Length(8, 30, message=u'密码限制在8-30字符之间')
    ])
    submit = SubmitField(u'重置密码')


class ChangeEmailRequestForm(FlaskForm):
    email = StringField(u'请输入邮箱', validators=[
        # 如果输入数据不是一个有效的邮箱，则弹出message
        Email(message=u'您输入的邮箱有误')])
    password = PasswordField(u'请输入你的密码', validators=[
        DataRequired(message=u'请输入一个有效数字！'),
        Length(8, 30, message=u'密码限制在8-30字符之间')
    ])
    submit = SubmitField(u'更换邮箱')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'该邮箱已被注册')








