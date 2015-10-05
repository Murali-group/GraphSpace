import bcrypt
from graphs.util import db
    
def authenticate(username=None, password=None):
    # check the username/password and return a User
    user = db.emailExists(username)

    if user != None:
        hashed_pw = user[1]
        
        #check password. if the password matches, return a
        #User object with associated information
        if bcrypt.hashpw(password, hashed_pw) == hashed_pw:
            user_obj = {}
            user_obj['user_id'] = user[0]
            user_obj['password'] = user[1]
            user_obj['activated'] = user[2]
            user_obj['activate_code'] = user[3]
            user_obj['public'] = user[4]
            user_obj['unlisted'] = user[5]
            user_obj['admin'] = user[6]

            return user_obj
    else:
        return None

