# coding=utf8


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, RadioField, PasswordField, SelectField
from wtforms.validators import NumberRange, DataRequired, Email, EqualTo, Length


class NameForm(FlaskForm):
    name = StringField(u'你的名字?', validators=[
        # 如果没有输入数据，则弹出message
        DataRequired(message=u'请输入一个有效数字！'),
        # 如果输入数据长度不在范围内，则弹出message
        Length(3, 30, message=u'用户名限制在6-12字符之间')
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
    age = IntegerField(u'你的年龄？', validators=[
        DataRequired(message=u'请输入一个有效数字！'),
        # 如果输入数字不在范围内，则弹出message
        NumberRange(18, 100, u'请输入18~100以内的数字！')])
    # choices中的元组里面的值可以为字符串，不能为数字，否则form.validate_on_submit()一直未false
    # 且form.errors中报错Not a valid choice
    users = RadioField(u'用户组', choices=[
        ('0', 'admin'), ('1', 'User')], default='0')
    # language = SelectField(u'Programming Language', choices=[('cpp', 'C++'), ('py', 'Python'),\
    #                                  ('text', 'Plain Text')])
    email = StringField(u'请输入邮箱', validators=[
        # 如果输入数据不是一个有效的邮箱，则弹出message
        Email(message=u'您输入的邮箱有误')])
    submit = SubmitField(u'注册or登陆')
