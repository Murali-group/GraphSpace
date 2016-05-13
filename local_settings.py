import random
import sys
import subprocess
import urllib2
import time
import os

'''
	This file sets all the environment variables for GraphSpace.
	All variables are imported in graphspace/settings.py
'''

# variables for setting up account through which GraphSpace emails
EMAIL_HOST='NONE'
EMAIL_HOST_USER='NONE'
EMAIL_HOST_PASSWORD='NONE'

# If error is thrown, display the error in the browser (ONLY FOR LOCAL MACHINES)
DEBUG=True
TEMPLATE_DEBUG=True

# URL through which to access graphspace
URL_PATH="http://localhost:8000/"

# If tracking is enabled for GraphSpace in Google Analytics
GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-00000000-0'

# Keys given by creating a requestor account on Amazon Mechanical Turk (https://www.mturk.com/mturk/welcome)
AWSACCESSKEYID='None'
SECRETKEY='None'

# Path to GraphSPace
PATH = "/Path_to_GraphSpace"

# SHOULD NEVER CHANGE THIS VALUE
SECRET_KEY= 'None'

# If needing to test on production mturk account (real money)
#AWS_URL = 'https://mechanicalturk.amazonaws.com'

# Sandbox (development) MTURK (fake money used)
AWS_URL = 'https://mechanicalturk.sandbox.amazonaws.com'

def getEmailHost():
	global EMAIL_HOST
	return EMAIL_HOST

def getEmailUser():
	global EMAIL_HOST_USER
	return EMAIL_HOST_USER

def getEmailPassword():
	global EMAIL_HOST_PASSWORD
	return EMAIL_HOST_PASSWORD

def getDebug():
	global DEBUG
	return DEBUG

def getTemplateDebug():
	global TEMPLATE_DEBUG
	return TEMPLATE_DEBUG

def getURLPath():
	global URL_PATH
	return URL_PATH

def getSecretKey():
	global SECRET_KEY
	return SECRET_KEY

def getGoogleAnalyticsId():
	global GOOGLE_ANALYTICS_PROPERTY_ID
	return GOOGLE_ANALYTICS_PROPERTY_ID

def getAWSKey():
	global AWSACCESSKEYID
	return AWSACCESSKEYID

def getAWSSecretKey():
	global SECRETKEY
	return SECRETKEY

def getPathToGS():
	global PATH
	return PATH

def getAWSURL():
	global AWS_URL
	return AWS_URL

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

'''
	If this file is ran, then it installs all the required packages.
	Need to only run this once upon installation.
'''
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

	import pip
	required_packages = ["django", "py-bcrypt","sqlalchemy","django-analytical","poster","networkx", "Sphinx"]
	installed_packages = sorted(["%s" % (i.key) for i in pip.get_installed_distributions()])

	# Installs any packages that are not already installed on the system
	for package in required_packages:
		if package not in installed_packages:
			install(package)

	import django
	version =  django.VERSION

	global SECRET_KEY
	SECRET_KEY = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])

	# Depending on the version, use appropriate command to sync databases
	if version[0] == 1 and version[1] > 7:
		migrate()
	else:
		syncdb()

	print "All dependencies have successfully been installed.  Please type 'python manage.py runserver' to start GraphSpace server on a local machine"
