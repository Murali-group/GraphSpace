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

def launch_server():
	subprocess.check_output([sys.executable, "manage.py", "runserver"])

def run_tests():
	os.system("python tests/restapi_test.py")

def install(package):
    pip.main(["install", package])		

if __name__ == "__main__":
	get_pip()

	install("django")
	install("py-bcrypt")
	install("django-analytical")

	# subprocess.check_call(["mv", "startup.db", "graphspace.db"])
	subprocess.check_call([sys.executable, "manage.py", "migrate"])

	print "All dependencies have successfully been installed."
	print "\n"
	print "**Please modify all environtment variables in gs-setup.sh and run command: '. gs-setup.sh' **"
