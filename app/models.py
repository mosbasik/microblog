from app import db
from hashlib import md5

ROLE_USER = 0
ROLE_ADMIN = 1


class User(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    nickname  = db.Column(db.String(64), index=True, unique=True)
    email     = db.Column(db.String(120), index=True, unique=True)
    role      = db.Column(db.SmallInteger, default=ROLE_USER)
    posts     = db.relationship('Post', backref='author', lazy='dynamic')
    about_me  = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)

    def is_authenticated(self):
        '''
        In general this method should return True unless the object represents a
        user that should not be allowed to authenticate for some reason.
        '''
        return True

    def is_active(self):
        '''
        Should return True for users unless they are inactive, for example
        because they have been banned.
        '''
        return True

    def is_anonymous(self):
        '''
        Should return True only for fake users that are not supposed to log into
        the system.
        '''
        return False

    def get_id(self):
        '''
        Should return a unique identifier for the user, in unicode format.  We
        use the unique id generated by the database for this.
        '''
        return unicode(self.id)

    def __repr__(self):
        '''
        Returns a representation of the object.
        '''
        return '<User %r>' % (self.nickname)

    def avatar(self, size):
        '''
        Returns the URL of the user's gravatar image based on their email,
        scaled to the specified size.
        '''
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)
    
    @staticmethod
    def make_unique_nickname(nickname):
        '''
        Ensures that the nickname of the user is unique
        '''
        # if the proposed nickname is already unique, return it
        if User.query.filter_by(nickname=nickname).first() is None
            return nickname

        # otherwise, append increasingly large numbers on it until it's unique
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=nickname).first() is None:
                break
            version += 1
        return new_nickname



class Post(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    body      = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)