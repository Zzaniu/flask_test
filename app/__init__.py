# coding=utf8


from flask import Flask, render_template
# 用于末班
from flask_bootstrap import Bootstrap
# 用于email
from flask_mail import Mail
# 在浏览器中渲染日期和时间
from flask_moment import Moment
# 用于SQL
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()


login_manager = LoginManager()
# 提供不同的安全等级防止用户会话遭篡改
# 设为'strong' 时，Flask-Login 会记录客户端IP地址和浏览器的用户代理信息，
# 如果发现异动就登出用户
login_manager.session_protection = 'strong'
# 设置登录页面的端点,因为再蓝图中，所以要加上前缀auth，类似url_for在蓝图中要加上前缀
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    # 导入配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    # 导入蓝本
    from .main import main as main_blueprint
    # 注册蓝本
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    # url_prefix参数：定义的路由需加上这个前缀
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
