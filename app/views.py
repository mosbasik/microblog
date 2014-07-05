from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid

from forms import LoginForm, EditForm, PostForm
from models import User, ROLE_USER, ROLE_ADMIN, Post
from datetime import datetime
from config import POSTS_PER_PAGE


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data,
                    timestamp=datetime.utcnow(),
                    author=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False).items
    return render_template('index.html',
                           title='Home',
                           user=g.user,
                           form=form,
                           posts=posts)


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    # if the user already exists and is authenticated, redirect to main page
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))

    # serve the login form
    form = LoginForm()

    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname','email'])
        #flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
        #return redirect('/index')

    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@oid.after_login
def after_login(resp):
    # without a valid email no one can log in
    if resp.email is None or resp.email == "":
        flash('Invalid login.  Please try again.')
        return redirect(url_for('login'))

    # search database for this email
    user = User.query.filter_by(email=resp.email).first()

    # if we don't have this email, create a new user
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname,
                    email=resp.email,
                    role=ROLE_USER)
        db.session.add(user)
        db.session.commit()
        db.session.add(user.follow(user)) # make the user follow himself
        db.session.commit()
    
    # load the remember_value from the session
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)

    # register that this is a valid login
    login_user(user, remember=remember_me)

    # redirect to the next page, or main page if no next specified
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    posts = [
        {'author':user, 'body':'Test post #1'},
        {'author':user, 'body':'Test post #2'}
    ]
    posts = user.posts.order_by(Post.timestamp.desc())
    return render_template('user.html',
                           user=user,
                           posts=posts)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html',
                           form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()

    # if the user doesn't exist
    if user is None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))

    # if the searched user is the logged in user
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('index'))

    # otherwise try to follow the user
    u = g.user.follow(user)

    # if it doesn't work for some reason, show an error message
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('index'))
    
    # commit changes and take us to their page
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    return redirect(url_for('user', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()

    # if the user doesn't exist
    if user is None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))

    # if the searched user is the logged in user
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('index'))

    # otherwise try to unfollow the user
    u = g.user.unfollow(user)

    # if it doesn't work for some reason, show an error message
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('index'))
    
    # commit changes and take us to their page
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '!')
    return redirect(url_for('user', nickname=nickname))