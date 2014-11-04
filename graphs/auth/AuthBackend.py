from sqlalchemy.orm.exc import NoResultFound
import bcrypt
from graphs.util.db_conn import Database
import graphs.models as models


class AuthBackend(object):
    '''
    Custom authentication backend for Django.

    http://docs.djangoproject.com/en/dev/topics/auth/customizing
    '''
    def __init__(self):
        #grab database information
        # using test database for hashing, because the original
        # hash algorithm used in Perl version of GraphSpace
        # is not accessible in Python.
        self.db = Database('test')
    
    def authenticate(self, username=None, password=None):
        # check the username/password and return a User
        print 'authenticating'
        try:
            print 'username: ' + username
            User = self.db.meta.tables['user']
            user = self.db.session.query(User).filter(User.c.user_id==username).one()
            hashed_pw = user.password
            
            #check password. if the password matches, return a
            #User object with associated information
            if bcrypt.hashpw(password, hashed_pw) == hashed_pw:
                user_obj = models.User()
                user_obj.user_id = user[0]
                user_obj.password = user[1]
                user_obj.activated = user[2]
                user_obj.activate_code = user[3]
                user_obj.public = user[4]
                user_obj.unlisted = user[5]
                user_obj.admin = user[6]
                return user_obj

        except NoResultFound:
            print 'no result found'  
            return None

    def get_user(self, uid):
        '''
            Queries the databases for the given user id. Return the matching user if the user id exists.
        '''
        try:
            User = self.db.meta.tables['user'];
            user = self.db.session.query(User).filter_by(user_id=uid).one()
        except NoResultFound:
            return None

        return user

    def has_perm(self, user_obj, perm, obj=None):
        return True