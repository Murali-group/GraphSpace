#!/usr/local/bin/python

import sqlite3
import datetime
import os
import hmac
from hashlib import sha1
import urllib2, urllib
import requests
import xml.etree.ElementTree as ET

'''
	Removes all public graphs uploaded anonymously (without a user logging into GraphSpace) 
	that are older than 30 days.

	@param cur: Database cursor
'''

SECRETKEY = os.environ.get('SECRETKEY')
AWSACCESSKEYID = os.environ.get('AWSACCESSKEYID')
PATH = "/home/divit/Documents/GRA/GraphSpace/"
PAYWORKERPATH = 'graphs/static/payWorkers.txt'
AWS_URL = 'https://mechanicalturk.sandbox.amazonaws.com'

def removeExpiredPublicGraphs(cur):
	cur.execute('select graph_id, user_id, created, public from graph where user_id like ?', ("%Public_User%temp.com", ))
	graphs = cur.fetchall()

	if graphs == None:
		return

	if len(graphs) == 0:
		return

	for graph in graphs:
		graph_id = graph[0]
		user_id = graph[1]
		created = datetime.datetime.strptime(graph[2], '%Y-%m-%d %H:%M:%S.%f')

		if created < datetime.datetime.now() + datetime.timedelta(days=-30):
			print "Deleting expired public graph:", graph_id, "owned by:", user_id 
			cur.execute('delete from graph where graph_id = ? and user_id = ?', (graph_id, user_id))

'''
	Removes all tasks that are older than 3 days.

	@param cur: Database cursor
'''
def removeExpiredTasks(cur):
	cur.execute('select * from task')
	tasks = cur.fetchall()

	if tasks == None:
		return

	if len(tasks) == 0:
		return

	for task in tasks:

		task_id = task[0]
		task_owner = task[1]
		user_id = task[2]
		graph_id = task[3]
		created = datetime.datetime.strptime(task[5], '%Y-%m-%d %H:%M:%S.%f')

		if created < datetime.datetime.now() + datetime.timedelta(days=-3):
			print "Deleting expired task owned by", task_owner, "for graph:", graph_id, "owned by", user_id 
			cur.execute('delete from task where task_id = ?', (task_id, ))

def generateTimeStampAndSignature(secretKey, operation):
	'''
		Generates common parameters as defined in (http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_CommonParametersArticle.html)

		@param secretKey: Secret Key given by AWS when creating account
		@param operation: Operation of call (http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_OperationsArticle.html)
		@return (Timestamp, Signature) following AWS semantics
	'''

	# Get current timestamp 
	cur_date = datetime.datetime.utcnow()
	timestamp = datetime.datetime.strftime(cur_date, "%Y-%m-%dT%H:%M:%S") + "Z"

	# Create signature based on service, operation and timestamp
	signature = "AWSMechanicalTurkRequester" + operation + timestamp

	# Encrypt with HMAC-SHA1 in base64, then URL encode
	# (http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMechanicalTurkRequester/MakingRequests_RequestAuthenticationArticle.html#CalcReqSig)
	signature = hmac.new(secretKey, signature, sha1).digest().encode("base64").rstrip("\n")
	signature = urllib.urlencode({"code": signature})[5:]

	return (timestamp, signature)

def forceExpireHIT(hitId):
	timestamp, signature = generateTimeStampAndSignature(os.environ.get('SECRETKEY'), "ForceExpireHIT")

	# Current as of 12/14/2016
	version = "2014-08-15"
	operation = "ForceExpireHIT"

	request = 'https://mechanicalturk.sandbox.amazonaws.com/?Service=AWSMechanicalTurkRequester&Operation=' + operation + '&AWSAccessKeyId=' + os.environ.get('AWSACCESSKEYID') + '&Version=' + version + '&Timestamp=' + timestamp + '&HITId=' + hitId + '&Signature=' + signature
	response = requests.get(request, allow_redirects=False)
	print response.text

def payWorkers(hitId, taskCode, cur):
	'''
		If hitID and taskCode pair exist in task_code table, pay them. 
		Otherwise, reject their answer.

		@param hitId: ID OF HIT 
		@param taskCode: Task code submitted by user
	'''
	# If the proper environment variables are set in gs-setup
	if os.environ.get('AWSACCESSKEYID') != None and os.environ.get('SECRETKEY') != None:

		# Get common parameters
		timestamp, signature = generateTimeStampAndSignature(os.environ.get('SECRETKEY'), "GetAssignmentsForHIT")

		# # Create database connection
		# db_session = data_connection.new_session()

		# Current as of 12/14/2016
		version = "2014-08-15"
		operation = "GetAssignmentsForHIT"

		# PAY ALL LAYOUT TASKS
		request = AWS_URL + '/?Service=AWSMechanicalTurkRequester&Operation=' + operation + '&AWSAccessKeyId=' + os.environ.get('AWSACCESSKEYID') + '&Version=' + version + '&Timestamp=' + timestamp + '&HITId=' + hitId + '&Signature=' + signature

		response = requests.get(request, allow_redirects=False)
		print response.text
		root = ET.fromstring(response.text)[1]
		for assignment in root.findall('Assignment'):
			assignment_id = ""
			worker_id = ""
			hit_id = ""
			assignment_status = ""
			task_code = ""

			assignment_id = assignment.find('AssignmentId').text
			worker_id = assignment.find('WorkerId').text
			hit_id = assignment.find('HITId').text
			assignment_status = assignment.find('AssignmentStatus').text
			task_code = ET.fromstring(assignment.find('Answer').text)[0][1].text

			# JUST PAY ALL THE WORKERS
			# Check to see if the task code exists and matches the hit id associated with it
			# cur.execute('select * from task_code as tc where tc.hit_id == ? and tc.code == ?', (hitId, task_code))
			# data = cur.fetchall()

			#if data == None or len(data) == 0:
			# 	# Reject them
			# 	timestamp, signature = generateTimeStampAndSignature(SECRETKEY, "RejectAssignment")
			# 	operation = "RejectAssignment"
			# 	request = AWS_URL + '/?Service=AWSMechanicalTurkRequester&Operation=' + operation + '&AWSAccessKeyId=' + AWSACCESSKEYID + '&Version=' + version + '&Timestamp=' + timestamp + '&AssignmentId=' + assignment_id + '&Signature=' + signature
			# else:
			# 	for code in data:
			# Get new signature and timestamp for different API call
			timestamp, signature = generateTimeStampAndSignature(SECRETKEY, "ApproveAssignment")
			operation = "ApproveAssignment"
			request = AWS_URL + '/?Service=AWSMechanicalTurkRequester&Operation=' + operation + '&AWSAccessKeyId=' + AWSACCESSKEYID + '&Version=' + version + '&Timestamp=' + timestamp + '&AssignmentId=' + assignment_id + '&Signature=' + signature
			
			# Delete task code from database so it can't be reused
			# cur.execute('delete from task_code where code = ? and hit_id =?', (code[1], code[0]))
			response = requests.get(request, allow_redirects=False)
			print response.text

def evaluateWork(cur):

	import os.path
	if os.path.isfile(PATH + PAYWORKERPATH):
	    worker_file = open(PATH + PAYWORKERPATH, 'r')

	    for line in worker_file:
	    	command = line.replace("\n", "").split('\t')
	    	print command
	    	if command[0] == "payWorkers":
	    		payWorkers(command[1], command[2], cur)

	    worker_file.close()
	    # os.remove(PATH + PAYWORKERPATH)

if __name__ == "__main__":
    conn = sqlite3.connect(PATH + 'graphspace.db')
    cur = conn.cursor()

    print "Running Cron Job to remove expired data from database"
    
    removeExpiredPublicGraphs(cur)
    removeExpiredTasks(cur)
    conn.commit()
    evaluateWork(cur)
    conn.commit()
    conn.close()
