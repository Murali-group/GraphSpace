from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import bcrypt

def create_account(form, database):
	'''
		Create a new account upon the validation of the following:

			- Id provided does not exist in the database.
			- Verify Password matches the Password given

		Additional constraints may be added:
			- minimum password length
			- include at least 1 capital letter
			- etc.

		@param form - the Register form
		@param database - GraphSpace database object

		For processing Django form, read section 'Processing the
		data from a form' at
		https://docs.djangoproject.com/en/1.6/topics/forms/
	'''
	

	# get the form data
	user_id = form.cleaned_data['user_id']
	password = form.cleaned_data['password']
	verify_password = form.cleaned_data['verify_password']

	# get user table from database
	users = database.meta.table['user']

    if password != verify_password:
        
    else:
        # 


	# query the database with the user_id provided
	# then verify that the user_id does not exist in the database
    session = database.new_session()



	# if verified:
	# 	hash the password
	# 	insert into the database the new account information
	# 	redirect to main page
	# else
	#   display error message
	#   clear the form(?)

	try:
    	# there is a matching user_id
    	check_user_id = session.query(users.c.id).filter(users.c.id==user_id).one()
    	# inform the user to try again
    except NoResultFound:
    	# there is no matching user_id
    	# create new user account.
    except MultipleResultsFound:
    	# this should not happen.
    	raise MultipleResultsFound
