import sys
import subprocess
import urllib2
import time
import pip
import os

def get_pip():
	response = urllib2.urlopen("https://bootstrap.pypa.io/get-pip.py")
	code = response.read()
	pip_file = open("get-pip.py", "w")
	pip_file.write(code)
	pip_file.close()
	subprocess.check_call(["sudo", sys.executable, "get-pip.py"])

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
	# sudo pip install django-analytical

	install("django")
	install("py-bcrypt")
	install("django-analytical")

	syncdb()
	
	print "All dependencies have successfully been installed.  Please type 'python manage.py runserver' to start GraphSpace server on a local machine"
