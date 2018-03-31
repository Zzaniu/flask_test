#!/usr/bin/env python
# coding=utf8


# 在编码程序的环境（虚拟环境中，一般是venv）上生成虚拟环境中安装的包（程序依赖的包）
# pip freeze >requirements.txt
# 在要部署的环境中，安装依赖的包
# pip install -r requirements.txt
#
# python manage.py db init 创建迁移仓库
# python manage.py db migrate 创建迁移脚本
# python manage.py db upgrade 执行迁移，生成表


import os
from app import create_app, db
from app.models import User, Role
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

# 用于shell中自动导入
manager.add_command("shell", Shell(make_context=make_shell_context))
# 用于迁移
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
