from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2
import json
import sqlite3 as lite
import bcrypt
import os

URL_PATH = "http://localhost:8000/"
DB_FULL_PATH = os.path.dirname(os.path.realpath("../graphspace.db")) + "/graphspace.db"

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj

def testCreateUser(email, password):
	register_openers()
	
	datagen, headers = multipart_encode({"user_id": email, "password": password})
	url = URL_PATH + "register/"
	
	request = urllib2.Request(url, datagen, headers)
	
	try:
		response = json.loads(urllib2.urlopen(request).read())

		if 'Error' in byteify(response):
			print "Error in testCreateUser: " + response['Error']
		else:
			print "Passed testCreateUser test!"
	except ValueError:
		print "Passed testCreateUser test!" 

def testRemoveUser(email, password):
	con = None
	try:
		con = lite.connect(DB_FULL_PATH)
		cur = con.cursor()

		cur.execute('select password from user where user_id = ?', (email, ))

		data = cur.fetchone()


		if data == None:
			print "Error in testRemoveUser: " + email + " does not exist!"
			return

		data_pw = data[0]

		if bcrypt.hashpw(password, data_pw) != data_pw:
			print "Error in testRemoveUser: Incorrect Password provided!"
			return;

		cur.execute('delete from user where user_id = ?', (email, ))
		con.commit()

		cur.execute('select user_id from user where user_id = ?', (email, ))

		data = cur.fetchone()

		if data == None:
			print "Passed testRemoveUser test!"
		else:
			print "Error in testRemoveUser: " + email + " did not get deleted successfully!"

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def testAddGraph(email, password, filename):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password, "graphname": open(filename, "r")})

	url = URL_PATH + "api/users/" + email + "/graph/add/" + filename + "/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testAddGraph: " + response['Error']
	else:
		print "Passed testAddGraph test!"

def testGetGraph(email, password, filename):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/users/" + email + "/graph/get/" + filename + "/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testAddGraph: " + response['Error']
	elif response['metadata']['name'] == 'Graph Name':
		print "Passed testGetGraph test!"
	else:
		print "Error in testAddGraph: Retrieved wrong JSON!"

def testGetGraphExists(email, password, filename):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/users/" + email + "/graph/exists/" + filename + "/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testGraphExists: " + response['Error']
	else:
		print "Passed testGraphExists test!"

def testUpdateGraph(email, password, filename):
	register_openers()
	
	orig_json = byteify(json.loads(open(filename, 'r').read()))
	orig_json['metadata']['name'] = "Testing Update"

	new_json = open('test.json', 'w+')
	new_json.write(json.dumps(orig_json, sort_keys=True, indent=4, separators=(',', ': ')))
	new_json.close()

	new_json = byteify(json.loads(open("test.json", 'r').read()))
	datagen, headers = multipart_encode({"username": email, "password": password, "graphname": open('test.json', "r")})
	url = URL_PATH + "api/users/" + email + "/graph/update/" + filename + "/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testUpdateGraph: " + response['Error']
	else:
		datagen, headers = multipart_encode({"username": email, "password": password})
		url = URL_PATH + "api/users/" + email + "/graph/get/" + filename + "/"
		
		request = urllib2.Request(url, datagen, headers)
		
		response = byteify(json.loads(urllib2.urlopen(request).read()))

		if 'Error' in response:
			print "Error in testUpdateGraph: " + response['Error']
		elif response['metadata']['name'] == 'Testing Update':
			print "Passed testUpdateGraph test!"
		else:
			print "Error in testUpdateGraph: Didn't Update JSON correctly!"

	os.remove("test.json")

def testGetUserGraphs(email, password):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/users/" + email + "/graphs/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testGetUserGraphs: " + response['Error']
	elif len(response['Graphs']) == 1:
		print "Passed testGetUserGraphs test!"
	else:
		print "Error in testGetUserGraphs: Incorrect number of graphs returned! Should be 1, got: ", response['Graphs']

def testMakeGraphPublic(email, password, filename):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/users/" + email + "/graph/makeGraphPublic/" + filename + "/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testMakeGraphPublic: " + response['Error']
	else:
		con = None
		try:
			con = lite.connect(DB_FULL_PATH)
			cur = con.cursor()

			cur.execute('select public from graph where graph_id = ? and user_id = ?', (filename, email))
			data = cur.fetchone()

			if data == None:
				print "Error in testMakeGraphPublic: " + filename + " does not exist!"

			isPublic = data[0]

			if isPublic == 1:
				print "Passed testMakeGraphPublic test!"
			else:
				print "Error in testMakeGraphPublic: " + filename + " is still not public!"

		except lite.Error, e:
			print 'Error %s:' % e.args[0]

		finally:
			if con:
				con.close()

def testMakeGraphPrivate(email, password, filename):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/users/" + email + "/graph/makeGraphPrivate/" + filename + "/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testMakeGraphPrivate: " + response['Error']
	else:
		con = None
		try:
			con = lite.connect(DB_FULL_PATH)
			cur = con.cursor()

			cur.execute('select public from graph where graph_id = ? and user_id = ?', (filename, email))
			data = cur.fetchone()

			if data == None:
				print "Error in testMakeGraphPrivate: " + filename + " does not exist!"

			isPublic = data[0]

			if isPublic == 0:
				print "Passed testMakeGraphPrivate test!"
			else:
				print "Error in testMakeGraphPrivate: " + filename + " is still not private!"

		except lite.Error, e:
			print 'Error %s:' % e.args[0]

		finally:
			if con:
				con.close()


def testRemoveGraph(email, password, filename):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/users/" + email + "/graph/delete/" + filename + "/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testRemoveGraph: " + response['Error']
	else:
		print "Passed testRemoveGraph test!"

def testCreateGroup(email, password, group_name):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/groups/add/" + email + "/" + group_name + "/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testCreateGroup: " + response['Error']
	else:
		print "Passed testCreateGroup test!"

def testGetGroup(email, password, group_name):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/groups/get/" + email + "/" + group_name + "/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testGetGroup: " + response['Error']
	elif response['Groups']['owner'] == email:
		print "Passed testGetGroup test!"
	else:
		print "Error in testGetGroup: Retrieved wrong group!"

def testAllGroupsForUser(email, password):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/users/" + email + "/groups/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testAllGroupsForUser: " + response['Error']
	elif len(response['Groups']) == 1:
		print "Passed testAllGroupsForUser test!"
	else:
		print "Error in testAllGroupsForUser: Retrieved wrong number of groups!"

def testAddUserToGroup(email, password, group_name, other_email):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/groups/" + email + "/group_name/adduser/" + other_email + "/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testAddUserToGroup: " + response['Error']
	else:
		print "Passed testAddUserToGroup test!"

def testRemoveUserFromGroup(email, password, group_name, other_email):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/groups/" + email + "/group_name/removeuser/" + other_email + "/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testRemoveUserFromGroup: " + response['Error']
	else:
		print "Passed testRemoveUserFromGroup test!"

def testShareGraphWithGroup(email, password, group_name, graph_name):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/users/graphs/" + graph_name + "/share/" + email + "/" + group_name + "/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testShareGraphWithGroup: " + response['Error']
	else:
		print "Passed testShareGraphWithGroup test!"

def testUnshareGraphWithGroup(email, password, group_name, graph_name):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/users/graphs/" + graph_name + "/unshare/" + email + "/" + group_name + "/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testUnshareGraphWithGroup: " + response['Error']
	else:
		print "Passed testUnshareGraphWithGroup test!"

def testRemoveGroup(email, password, group_name):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/groups/delete/" + email + "/" +  group_name + "/"
	
	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testRemoveGroup: " + response['Error']
	else:
		print "Passed testRemoveGroup test!"

def testGetTagsForUser(email, password):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/tags/user/" + email + "/"

	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testRemoveGroup: " + response['Error']
	elif response['Tags'][0] == 'tutorial':
		print "Passed testGetTagsForUser test!"
	else:
		print "Error in testGetTagsForUser: Retrived wrong JSON!"

def testGetTagsForGraph(email, password, graph_name):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/tags/user/" + email + "/" + graph_name + "/"

	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testRemoveGroup: " + response['Error']
	elif 'Tags' not in response: 
		print "No Tags Found!"
	elif response['Tags'][0] == 'tutorial':
		print "Passed testGetTagsForGraph test!"
	else:
		print "Error in testGetTagsForGraph: Retrived wrong JSON!"

def testMakeGraphsWithTagPublic(email, password, tag, filename):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/tags/user/" + email + "/" + tag + "/makePublic/"

	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testMakeGraphsWithTagPublic: " + response['Error']
	else:
		con = None
		try:
			con = lite.connect(DB_FULL_PATH)
			cur = con.cursor()

			cur.execute('select public from graph where graph_id = ? and user_id = ?', (filename, email))
			data = cur.fetchone()

			if data == None:
				print "Error in testMakeGraphsWithTagPublic: " + filename + " does not exist!"

			isPublic = data[0]

			if isPublic == 1:
				print "Passed testMakeGraphsWithTagPublic test!"
			else:
				print "Error in testMakeGraphsWithTagPublic: " + filename + " is still not public!"

		except lite.Error, e:
			print 'Error %s:' % e.args[0]

		finally:
			if con:
				con.close()


def testMakeGraphsWithTagPrivate(email, password, tag, filename):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/tags/user/" + email + "/" + tag + "/makePrivate/"

	request = urllib2.Request(url, datagen, headers)
	
	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testMakeGraphsWithTagPrivate: " + response['Error']
	else:
		con = None
		try:
			con = lite.connect(DB_FULL_PATH)
			cur = con.cursor()

			cur.execute('select public from graph where graph_id = ? and user_id = ?', (filename, email))
			data = cur.fetchone()

			if data == None:
				print "Error in testMakeGraphsWithTagPrivate: " + filename + " does not exist!"

			isPublic = data[0]

			if isPublic == 0:
				print "Passed testMakeGraphsWithTagPrivate test!"
			else:
				print "Error in testMakeGraphsWithTagPrivate: " + filename + " is still not private!"

		except lite.Error, e:
			print 'Error %s:' % e.args[0]

		finally:
			if con:
				con.close()

def testDeleteGraphsWithTag(email, password, tag):
	register_openers()
	
	datagen, headers = multipart_encode({"username": email, "password": password})
	url = URL_PATH + "api/tags/user/" + email + "/" + tag + "/delete/"

	request = urllib2.Request(url, datagen, headers)

	response = byteify(json.loads(urllib2.urlopen(request).read()))

	if 'Error' in response:
		print "Error in testDeleteGraphsWithTag: " + response['Error']

	con = None
	try:
		con = lite.connect(DB_FULL_PATH)
		cur = con.cursor()

		cur.execute('select * from graph_to_tag where tag_id = ? and user_id = ?', (tag, email))
		data = cur.fetchone()

		if data == None:
			print "Passed testDeleteGraphsWithTag test!"
		else:
			print "Error in testDeleteGraphsWithTag"

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

if __name__ == '__main__':

	email = "tester@test.com"
	password = "test"

	email_other = "tester2@test.com"
	password = "test"

	group_name = "test_group"
	graph_name = "example.json"

	tag = "tutorial"

	testCreateUser(email, password)
	testCreateUser(email_other, password)

	# Graph API Tests
	testAddGraph(email, password, graph_name)
	testGetGraph(email, password, graph_name)
	testGetGraphExists(email, password, graph_name)
	testUpdateGraph(email, password, graph_name)
	testMakeGraphPublic(email, password, graph_name)
	testMakeGraphPrivate(email, password, graph_name)
	testGetUserGraphs(email, password)

	# Group API Tests
	testCreateGroup(email, password, group_name)
	testGetGroup(email, password, group_name)
	testAllGroupsForUser(email, password)
	testAddUserToGroup(email, password, group_name, email_other)
	testRemoveUserFromGroup(email, password, group_name, email_other)
	testShareGraphWithGroup(email, password, group_name, graph_name)
	testUnshareGraphWithGroup(email, password, group_name, graph_name)
	testRemoveGroup(email, password, group_name)

	# Tags API Tests
	testGetTagsForUser(email, password)
	testGetTagsForGraph(email, password, graph_name)
	testMakeGraphsWithTagPublic(email, password, tag, graph_name)
	testMakeGraphsWithTagPrivate(email, password, tag, graph_name)
	testDeleteGraphsWithTag(email, password, tag)
	
	testRemoveUser(email, password)
	testRemoveUser(email_other, password)
