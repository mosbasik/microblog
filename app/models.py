from app import db
from hashlib import md5

ROLE_USER = 0
ROLE_ADMIN = 1


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    nickname  = db.Column(db.String(64), index=True, unique=True)
    email     = db.Column(db.String(120), index=True, unique=True)
    role      = db.Column(db.SmallInteger, default=ROLE_USER)
    posts     = db.relationship('Post', backref='author', lazy='dynamic')
    about_me  = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    followed  = db.relationship('User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

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
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() \
            + '?d=mm&s=' + str(size)

    def follow(self, user):
        '''
        Adds a new user to our following list.  Returns self on success or None
        on fail.
        '''
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        '''
        Removes a user from our following list.  Returns self on success or None
        on fail.
        '''
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        '''
        Return true if the specified user is in our following list at least once.
        '''
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    @staticmethod
    def make_unique_nickname(nickname):
        '''
        Ensures that the nickname of the user is unique
        '''
        # if the proposed nickname is already unique, return it
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname

        # otherwise, append increasingly large numbers on it until it's unique
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                return new_nickname
            version += 1


class Post(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    body      = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)