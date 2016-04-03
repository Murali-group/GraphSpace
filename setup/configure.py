import sys
import subprocess
import urllib2
import time
import os
import django

def get_pip():
	response = urllib2.urlopen("https://bootstrap.pypa.io/get-pip.py")
	code = response.read()
	pip_file = open("get-pip.py", "w")
	pip_file.write(code)
	pip_file.close()
	subprocess.check_call(["sudo", sys.executable, "get-pip.py"])
	os.remove("get-pip.py")

def migrate():
	subprocess.check_output([sys.executable, "manage.py", "migrate"])

def syncdb():
	subprocess.check_output([sys.executable, "manage.py", "syncdb", "--noinput"])

def run_tests():
	os.system("python tests/restapi_test.py")

def install(package):
	subprocess.call(["sudo", "pip", "install", package])

if __name__ == "__main__":
	get_pip()

	# IF ANY OF THE BELOW PACKAGES DO NOT INSTALL
	# PLEASE RUN FOLLOWING COMMANDS ON TERMINAL
	# sudo pip install django
	# sudo pip install py-bcrypt
	# sudo pip install sqlalchemy
	# sudo pip install django-analytical
	# sudo pip install poster
	# sudo pip install networkx
	# sudo pip install requests
	# sudo pip install numpy
	# sudo pip install scipy
	# sudo pip install scikit-learn

	import pip

	install("django")
	install("py-bcrypt")
	install("sqlalchemy")
	install("django-analytical")
	install("poster")
	install("networkx")
	install("requests")
	install("numpy")
	install("scipy")
	install("scikit-learn")

	version =  django.VERSION

	if version[0] == 1 and version[1] > 7:
		migrate()
	else:
		syncdb()

	print "All dependencies have successfully been installed.  Please type 'python manage.py runserver' to start GraphSpace server on a local machine"
