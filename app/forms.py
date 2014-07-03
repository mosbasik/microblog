from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField
from wtforms.validators import Required, Length
from app.models import User

class LoginForm(Form):
    openid = TextField('openid', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)

class EditForm(Form):
    nickname = TextField('nickname', validators=[Required()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        '''
        Custom validation method, overriding the default one.
        '''
        # if the form doesn't validate, return False
        if not Form.validate(self):
            return False

        # if the submitted nick is the same as the old nick, return True
        if self.nickname.data == self.original_nickname:
            return True

        # if the submitted nick already exists, raise error and return False
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user != None:
            self.nickname.errors.append('This nickname is already in use.  Please choose another one.')
            return False

        # otherwise the submitted nick is fine, return True
        return True

class PostForm(Form):
    post = TextField('post', validators=[Required()])