# coding=utf8


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, RadioField, PasswordField, SelectField, TextAreaField, BooleanField
from wtforms.validators import NumberRange, DataRequired, Email, EqualTo, Length, Regexp
from ..models import User, Role
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField


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


class EditProfileForm(FlaskForm):
    name = StringField(u'真实姓名', validators=[Length(0, 64)])
    age = IntegerField(u'你的年龄？', validators=[
        NumberRange(0, 200, u'请输入0~200以内的数字！')])
    location = StringField(u'家乡', validators=[Length(0, 64)])
    about_me = TextAreaField(u'自我介绍')
    submit = SubmitField(u'确认')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp(ur'^[A-Za-z0-9_\u4e00-\u9fa5]+$', 0, u'用户名只能包含字母数字下划线汉字')])
    confirmed = BooleanField(u'是否已确认')
    # coerce=int, 把字段的值转换为整数
    role = SelectField(u'用户组', coerce=int)
    name = StringField(u'真实姓名', validators=[Length(0, 64)])
    location = StringField(u'家乡', validators=[Length(0, 64)])
    about_me = TextAreaField(u'自我介绍')
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    # field是表单中传上来的数据，所以要用field.data
    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已经被注册.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已经被使用.')


# 帖子表单
class PostForm(FlaskForm):
    body = PageDownField(u'帖子正文', validators=[DataRequired()])
    submit = SubmitField(u'发布')


# 评论表单
class CommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField(u'提交')










