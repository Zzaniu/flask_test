# coding=utf8


from flask import render_template, session, redirect, url_for, flash, abort, request, make_response, current_app
from flask_login import login_required, current_user

from app.decorators import admin_required, permission_required
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from .. import db
from ..email import send_email
from ..models import User, Role, Permission, Post, Comment
from flask_sqlalchemy import get_debug_queries


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
        # session:请求上下文，用户会话，用于存储请求之间需要“记住”的值的词典
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


@main.route('/', methods=['GET', 'POST'])
def hello():
    form = PostForm()
    if current_user.can(Permission.WRITE) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    # current_user._get_current_object()获取当前对象
                    # 官方文档：返回当前对象。如果您想要在某个时间内实现代理的真实对象，
                    # 或者因为您想要将对象传递到不同的上下文，那么这将非常有用。
                    author=current_user._get_current_object()
                    )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.hello'))
    # request:请求上下文，请求对象，封装了客户端发出的HTTP 请求中的内容
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=30, error_out=False)
    posts = pagination.items
    # 按照时间戳进行降序排列
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('hello.html', form=form, posts=posts,\
                           pagination=pagination, show_followed=show_followed)


@main.route('/all')
@login_required
def show_all():
    # cookie 只能在响应对象中设置，因此这两个路由不能依赖Flask，要使用make_response()方法创建响应对象
    resp = make_response(redirect(url_for('.hello')))
    # 前两个参数分别是cookie 名和值。可选的max_age 参数设置cookie 的过期时间，单位为秒。
    # 如果不指定参数max_age，浏览器关闭后cookie 就会过期。
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.hello')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    # type=int 保证参数无法转换成整数时，返回默认值,即1
    page = request.args.get('page', 1, type=int)
    # 返回值是一个Pagination 类对象，这个类在Flask-SQLAlchemy 中定义
    # pagination的属性和方法见《Flask WEB》121页
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=10, error_out=False)
    # 当前页面中的记录
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts, pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.age = form.age.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash(u'你的信息已更新')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.age.data = current_user.age
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


# admin_required:只有管理员能进这个页面
# login_required:只有已经登录的用户才能进这个页面
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash(u'信息已经更新.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / 10 + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash(u'帖子已经更新.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效的用户.')
        return redirect(url_for('.index'))
    # 有问题，这个不弹出来。逻辑上来说，这是如果已经关注过这个用户，再点关注则弹出已经关注这个用户
    # 但是，模板里面已经有关注过这个用户则不显示关注按钮而显示取消关注按钮，所以此句存在无意义。
    # 暂且保留，待日后验证逻辑
    if current_user.is_following(user):
        flash(u'你已经关注这个用户.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash(u'你关注了%s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效的用户.')
        return redirect(url_for('.index'))
    # 有问题，同上 follow 中的问题
    if not current_user.is_following(user):
        flash(u'你还没有关注这个用户.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash(u'你取消关注%s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效的用户.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=30, error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效的用户.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, per_page=30, error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


# 查询
@main.after_app_request
def after_request(response):
    # get_debug_queries 函数返回一个列表，其元素是请求中执行的查询
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' % \
                (query.statement, query.parameters, query.duration, query.context))
    return response


