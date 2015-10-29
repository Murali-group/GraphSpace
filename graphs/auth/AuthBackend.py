import bcrypt
from graphs.util import db
    
def authenticate(username=None, password=None):
    # check the username/password and return a User
    user = db.emailExists(username)

    if user != None:
        hashed_pw = user.password
        
        #check password. if the password matches, return a
        #User object with associated information
        if bcrypt.hashpw(password, hashed_pw) == hashed_pw:
            user_obj = {}
            user_obj['user_id'] = user.user_id
            user_obj['password'] = user.password
            user_obj['activated'] = user.activated
            user_obj['activate_code'] = user.activate_code
            user_obj['public'] = user.public
            user_obj['unlisted'] = user.unlisted
            user_obj['admin'] = user.admin

            return user_obj
    else:
        return None

