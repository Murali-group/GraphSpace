import urllib2
import os

def get_pip():
	response = urllib2.urlopen("https://bootstrap.pypa.io/get-pip.py")
	code = response.read()
	pip_file = open("get-pip.py", "w")
	pip_file.write(code)
	pip_file.close()
	os.system('sudo python get-pip.py')

def install_django():
	os.system('sudo pip install django')

def install_py_bcrypt():
	os.system('sudo pip install py-bcrypt')

def install_google_analytics():
	os.system('sudo pip install django-analytical')

def change_db_name():
	os.system('mv startup.db graphspace.db')

def set_environment_variables():
	os.system('. gs-setup.sh')

def migrate_db():
	os.system('python manage.py migrate')

def tell_user_to_run_system():
	print "Software is now installed.  Type 'python manage.py runserver' to run GraphSpace!"

def install_dependencies():
	get_pip()
	install_django()
	install_py_bcrypt()
	change_db_name()
	set_environment_variables()
	migrate_db()
	tell_user_to_run_system()

if __name__ == '__main__':
	install_dependencies()