import os
from sensitive import MAIL_USERNAME
from sensitive import MAIL_PASSWORD

CSRF_ENABLED = True

SECRET_KEY = 'you-will-never-guess'

OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }
]

basedir = os.path.abspath(os.path.dirname(__file__))

# required by Flask-SQLAlchemy extension.  this is the path of our database file
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

# folder where we will store SQLAlchemy-migrate data files
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# mail server settings
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True

# administrator list
ADMINS = ['phenryextra@zoho.com']

# pagination
POSTS_PER_PAGE = 2

# name of the full text search database
WHOOSH_BASE = os.path.join(basedir, 'search.db')

MAX_SEARCH_RESULTS = 50