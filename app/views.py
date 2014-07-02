from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm
from models import User, ROLE_USER, ROLE_ADMIN


@app.route('/')
@app.route('/index')
def index():
    user = {'nickname':'Miguel'}
    posts = [ # fake array of posts
        { 
            'author': { 'nickname': 'John' }, 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'author': { 'nickname': 'Susan' }, 
            'body': 'The Avengers movie was so cool!' 
        }
    ]
    return render_template('index.html',
                           title = 'Home',
                           user = user,
                           posts = posts)


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
        user = User(nickname=nickname,
                    email=resp.email,
                    role=ROLE_USER)
        db.session.add(user)
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