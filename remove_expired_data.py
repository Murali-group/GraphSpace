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
		created = datetime.datetime.strptime(task[6], '%Y-%m-%d %H:%M:%S.%f')

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

def payTaskWorkers(hitID, worked_layout, cur):
	'''
		Pay all assignments(work done by MTURk workers) for a particular graph
		@param hitID: ID of HIT for MTURK
		@param worked_layout: Name of layout
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
		request = 'https://mechanicalturk.sandbox.amazonaws.com/?Service=AWSMechanicalTurkRequester&Operation=' + operation + '&AWSAccessKeyId=' + os.environ.get('AWSACCESSKEYID') + '&Version=' + version + '&Timestamp=' + timestamp + '&HITId=' + hitID + '&Signature=' + signature

		response = requests.get(request, allow_redirects=False)

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

			cur.execute('select * from task_code as tc where tc.hit_id == ? and tc.code == ?', (hitID, task_code))
			data = cur.fetchall()

			if data == None or len(data) == 0:
				# Reject them
				timestamp, signature = generateTimeStampAndSignature(SECRETKEY, "RejectAssignment")
				operation = "RejectAssignment"
				request = 'https://mechanicalturk.sandbox.amazonaws.com/?Service=AWSMechanicalTurkRequester&Operation=' + operation + '&AWSAccessKeyId=' + AWSACCESSKEYID + '&Version=' + version + '&Timestamp=' + timestamp + '&AssignmentId=' + assignment_id + '&Signature=' + signature
			else:
				for code in data:
					# Get new signature and timestamp for different API call
					timestamp, signature = generateTimeStampAndSignature(SECRETKEY, "ApproveAssignment")
					operation = "ApproveAssignment"
					request = 'https://mechanicalturk.sandbox.amazonaws.com/?Service=AWSMechanicalTurkRequester&Operation=' + operation + '&AWSAccessKeyId=' + AWSACCESSKEYID + '&Version=' + version + '&Timestamp=' + timestamp + '&AssignmentId=' + assignment_id + '&Signature=' + signature
					# Delete task code from database so it can't be reused
					cur.execute('delete from task_code where code = ?', (code[1],))
					print code[1]
			response = requests.get(request, allow_redirects=False)

			print response.text
		
def payApproveWorkers(hitId, worked_layout, cur):
	'''
		Pay all assignments(work done by MTURk workers) for a approval tasks for a graph
		@param hitID: ID of HIT for MTURK
		@param worked_layout: Name of layout
	'''
	payTaskWorkers(hitId, worked_layout, cur)
	cur.execute('delete from approve_task where approve_hit_id = ?', (hitId))

def payWorkers(cur):

	import os.path
	os.path.isfile("payWorkers.txt") 

	worker_file = open('payWorkers.txt', 'r')

	for line in worker_file:
		command = line.replace("\n", "").split('\t')
		if command[0] == "payTaskWorkers" or command[0] == "payApproveWorkers":
			payTaskWorkers(command[1], command[2], cur)

	worker_file.close()
	os.remove("payWorkers.txt")

if __name__ == "__main__":
    conn = sqlite3.connect('graphspace.db')
    cur = conn.cursor()

    print "Running Cron Job to remove expired data from database"
    
    removeExpiredPublicGraphs(cur)
    removeExpiredTasks(cur)
    payWorkers(cur)

    conn.commit()
    conn.close()
