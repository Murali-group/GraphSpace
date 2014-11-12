import sqlite3 as lite
from django.core.mail import send_mail
from datetime import datetime
import sys
import bcrypt
import json

# This file is a wrapper to communicate with sqlite3 database 
# that does not need authentication for connection

def is_admin(username):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select admin from user where user_id = ?', (username,))

		data = cur.fetchone()[0]

		if data == None:
			return None
		else:
			if data == 1:
				return True
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def user_exists(username, password):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select password from user where user_id = ?', (username,))

		data = cur.fetchone()[0]

		if data == None:
			return None
		else:
			if bcrypt.hashpw(password, data) != data:
				return None
			else:
				return username

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

# Inserts a uniquely named graph under a username
def insert_graph(username, graphname, graph_json):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select graph_id from graph where user_id = ? and graph_id = ?', (username, graphname))

		data = cur.fetchone()

		if data == None:
			curTime = datetime.now()
			cur.execute('insert into graph values(?, ?, ?, ?, ?, ?, ?)', (graphname, username, graph_json, curTime, curTime, 0, 1))
			con.commit()

			graphJson = json.loads(graph_json)
			tags = graphJson['metadata']['tags']

			for tag in tags:
				cur.execute('select tag_id from graph_tag where tag_id=?', (tag, ))
				tagData = cur.fetchone()
				if tagData == None:
					cur.execute('insert into graph_tag values(?)', (tag, ))

				cur.execute('insert into graph_to_tag values(?,?,?)', (graphname, username, tag))
				con.commit()

			edges = graphJson['graph']['data']['edges']

			for edge in edges:
				cur.execute('insert into edge values(?,?,?,?,?,?,?,?)', (username, graphname, edge["source"], graphname, graphname, edge["target"], edge["source"] + "-" + edge["target"], edge["directed"]))
				con.commit()

			nodes = graphJson['graph']['data']['nodes']

			for node in nodes:
				cur.execute('insert into node values(?,?,?,?)', (node['id'], node['label'], username, graphname))
				con.commit()

			return None
		else:
			return 'Graph Already Exists!'

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

#Gets the graph's json
def get_graph(username, graphname):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select json from graph where user_id = ? and graph_id = ?', (username, graphname))

		rowData = cur.fetchone()

		if rowData == None:
			return None

		data = rowData[0]

		if data != None:
			return data
		else:
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

# Deletes graph from database
def delete_graph(username, graphname):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()

		cur.execute('delete from graph where user_id = ? and graph_id = ?', (username, graphname))
		con.commit()

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

# Get all graphs for username
def get_all_graphs(username):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select graph_id from graph where user_id = ?', (username, ))

		data = cur.fetchall()

		if data == None:
			return None

		cleaned_data=[]
		for graphs in data:
			graphs = str(graphs[0])
			cleaned_data.append(graphs)

		if cleaned_data != None:
			return cleaned_data

		else:
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def get_all_groups():
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select * from \"group\"');

		data = cur.fetchall()

		if data == None:
			return None

		cleaned_data = []

		for record in data:
			cleaned_record = []
			cleaned_record.append(record[2])
			cleaned_record.append(record[0])
			cleaned_record.append(record[3])
			cleaned_data.append(cleaned_record)

		return cleaned_data
	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def get_group_by_id(group):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select description, owner_id from \"group\" where group_id=?', (group, ));

		data = cur.fetchall()

		cleaned_data = []

		for row in data:
			members = get_group_members(group)
			tuple_list = (str(row[0]), members, str(row[1]))
			cleaned_data.append(tuple_list)

		return cleaned_data
	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def get_group_members(group):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select user_id from group_to_user where group_id=?', (group, ));

		data = cur.fetchall()

		cleaned_data = []
		for member in data:
			cleaned_data.append(str(member[0]))

		return cleaned_data
	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def remove_group(owner, group):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select owner_id from \"group\" where owner_id=? and group_id=?', (owner, group, ));

		data = cur.fetchone()
		if data == None:
			return "Group not found!"

		val = data[0]

		if val == None:
			return "Can't remove group"
		else:
			cur.execute('delete from \"group\" where owner_id=? and group_id=?', (owner, group, ))
			cur.execute('delete from group_to_user where group_id=?', (group, ))
			con.commit();
			return "Group removed!"

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

# Inserts a uniquely named graph under a username
def create_group(username, group):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select group_id from \"group\" where group_id=?', (group, ));

		data = cur.fetchone()

		if data == None:
			cur.execute('insert into \"group\" values(?, ?, ?, ?, ?, ?)', (group, group, username, "", 0, 1))
			cur.execute('insert into group_to_user values(?, ?)', (username, group, ))
			con.commit()
			return "Created!"
		else:
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

#Gets all information about the group that user belongs to
def info_groups_for_user(username):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select group_id, description, owner_id, public from group_to_user where user_id=?', (username, ))

		data = cur.fetchall()

		cleaned_data=[]
		for groups in data:
			groups = str(groups[0])
			cleaned_data.append(groups)

		return cleaned_data

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()
#Get all groups a user belongs to
def groups_for_user(username):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select group_id from group_to_user where user_id=?', (username, ))

		data = cur.fetchall()

		cleaned_data=[]
		for groups in data:
			groups = str(groups[0])
			cleaned_data.append(groups)

		return cleaned_data

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def add_user_to_group(username, owner, group):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select user_id from user where user_id=?', (username, ))

		data = cur.fetchone()[0]
		if data == None:
			return "User does not exist!"

		cur.execute('select group_id from group_to_user where user_id=? and group_id=?', (owner, group, ))
		isOwner = cur.fetchone()[0]

		if isOwner != None:
			cur.execute('insert into group_to_user values(?, ?)', (username, group, ))
			con.commit();
			return "User added!"
		else:
			return "Add yourself to the group first!"

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def remove_user_from_group(username, owner, group):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select user_id from user where user_id=?', (username, ))
		data = cur.fetchone()[0]
		if data == None:
			return "User does not exist!"

		cur.execute('select owner_id from \"group\" where owner_id=? and group_id=?', (owner, group, ))
		isOwner = cur.fetchone()[0]
		if isOwner != None:
			cur.execute('delete from group_to_user where user_id=? and group_id=?', (username, group, ))
			con.commit();
			return "User removed!"
		else:
			return "Can't delete user from a group you are not the owner of!"

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def share_with_group(owner, graph, group):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select user_id from graph where user_id=? and graph_id=?', (owner, graph, ))
		isOwner = cur.fetchone()[0]
		if isOwner != None:
			cur.execute('select user_id from group_to_user where user_id=? and group_id=?', (owner, group, ))
			isMember = cur.fetchone()[0]
			if isMember != None:
				cur.execute('insert into group_to_graph values(?, ?, ?)', (group, graph, owner, ))
				con.commit()
				return "Graph successfully shared!"
			else:
				return "You are not a member of this group!"
		else:
			return "You don't own this graph!"

	except lite.Error, e:
		print 'Error %s:' % e.args[0]

	finally:
		if con:
			con.close()

def unshare_with_group(owner, graph, group):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select user_id from graph where user_id=? and graph_id=?', (owner, graph, ))
		isOwner = cur.fetchone()[0]
		if isOwner != None:
			cur.execute('select user_id from group_to_user where user_id=? and group_id=?', (owner, group, ))
			isMember = cur.fetchone()[0]
			if isMember != None:
				cur.execute('delete from group_to_graph where group_id=? and graph_id=? and user_id=?', (group, graph, owner))
				con.commit()
				return "Graph successfully unshared!"
			else:
				return "You are not a member of this group!"
		else:
			return "You don't own this graph!"

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def get_shared_graphs(user, tags):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		if tags:
			cur.execute('select distinct g.graph_id, g.modified, g.user_id, g.public from group_to_user as gu, graph as g, graph_to_tag as gt, group_to_graph as gg where gg.group_id = gu.group_id and gt.graph_id=g.graph_id and gg.graph_id=g.graph_id and gu.user_id=?', (user, ))
		else:
			cur.execute('select distinct g.graph_id, g.modified, g.user_id, g.public from group_to_user as gu, graph as g, group_to_graph as gg where gg.group_id = gu.group_id and gg.graph_id=g.graph_id and gu.user_id=?', (user, ))
		graphs = cur.fetchall()

		cleaned_graph = []
		for graph in graphs:
			cur.execute('select tag_id from graph_to_tag where graph_id=? and user_id=?', (graph[0], graph[2]))
			tags = cur.fetchall()
			cleanedtags = []

			for tag in tags:
				cleanedtags.append(str(tag[0]))

			graph_list = list(graph)
			if len(cleanedtags) > 0:
				# for tag in tags:
				graph_list.insert(1, cleanedtags)
				cleaned_graph.append(tuple(graph_list))
			else:
				graph_list.insert(1, "")
				cleaned_graph.append(tuple(graph_list))

		print cleaned_graph
		if cleaned_graph != None:
			return cleaned_graph
		else:
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def get_graph_info(username, tags):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()

		if tags:
			cur.execute('select distinct g.graph_id, g.modified, g.user_id, g.public from graph as g, graph_to_tag as gt where g.user_id=? and gt.tag_id=? and g.graph_id = gt.graph_id', (username, tags))
		else:
			cur.execute('select distinct g.graph_id, g.modified, g.user_id, g.public from graph as g where g.user_id=?', (username, ))

		graphs = cur.fetchall()
		
		cleaned_graph = []
		for graph in graphs:
			cur.execute('select tag_id from graph_to_tag where graph_id=? and user_id=?', (graph[0], graph[2]))
			tags = cur.fetchall()
			cleanedtags = []

			for tag in tags:
				cleanedtags.append(str(tag[0]))

			graph_list = list(graph)
			if len(cleanedtags) > 0:
				# for tag in tags:
				graph_list.insert(1, cleanedtags)
				cleaned_graph.append(tuple(graph_list))
			else:
				graph_list.insert(1, "")
				cleaned_graph.append(tuple(graph_list))

		if cleaned_graph != None:
			return cleaned_graph
		else:
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def get_public_graph_info(tags):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		if tags:
			cur.execute('select distinct g.graph_id, g.modified, g.user_id, g.public from graph as g where g.public=?', (1, ))
		else:
			cur.execute('select distinct g.graph_id, g.modified, g.user_id, g.public from graph as g, graph_to_tag as gt where g.public=? and gt.graph_id = g.graph_id', (1, ))
		graphs = cur.fetchall()
		
		cleaned_graph = []
		for graph in graphs:
			cur.execute('select tag_id from graph_to_tag where graph_id=? and user_id=?', (graph[0], graph[2]))
			tags = cur.fetchall()
			cleanedtags = []

			for tag in tags:
				cleanedtags.append(str(tag[0]))


			if len(cleanedtags) > 0:
				# for tag in tags:
				graph_list = list(graph)
				graph_list.insert(1, cleanedtags)
				cleaned_graph.append(tuple(graph_list))

		if cleaned_graph != None:
			return cleaned_graph
		else:
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()


def get_all_graph_info(tags):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select distinct g.graph_id, g.modified, g.user_id, g.public from graph as g')
		graphs = cur.fetchall()
		cleaned_graph = []
		for graph in graphs:
			cur.execute('select tag_id from graph_to_tag where graph_id=? and user_id=?', (graph[0], graph[2]))
			tags = cur.fetchall()
			cleanedtags = []

			for tag in tags:
				cleanedtags.append(str(tag[0]))


			if len(cleanedtags) > 0:
				# for tag in tags:
				graph_list = list(graph)
				graph_list.insert(1, cleanedtags)
				cleaned_graph.append(tuple(graph_list))

		if cleaned_graph != None:
			return cleaned_graph
		else:
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()


def get_all_groups_for_this_graph(graph):
	global SERVER_URL
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute('select group_id from group_to_graph where graph_id=?', (graph, ))
		graphs = cur.fetchall()
		
		cleaned_graphs = []
		if graphs != None:
			for graph in graphs:
				cleaned_graphs.append(str(graph[0]))
			return cleaned_graphs
		else:
			return None

	except lite.Error, e:
		print 'Error %s:' % e.args[0]
		return None

	finally:
		if con:
			con.close()

def emailExists(email):
	con = None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute("select user_id from user where user_id = ?", [email])

		if cur.rowcount == 0:
			return None

		data = cur.fetchone()
		return data

	except lite.Error, e:
   
    		print "Error %s:" % e.args[0]

	finally:
		if con:
			con.close()


def sendForgotEmail(email):

	if emailExists(email) != None:
		con=None
		try:
			con = lite.connect('test.db')

			cur = con.cursor()
			cur.execute("select password from user where user_id = ?", [email])

			if cur.rowcount == 0:
				return None

			data = cur.fetchone()

			# msg = MIMEText("Please go to the following url to reset your password: http://localhost:8000/reset?id=" + data[0])
			# msg["Subject"] = 'GraphSpace Reset Password'
			# msg["From"] = 'GraphSpace Admin'
			# msg["To"] = email

			# smtpserver = smtplib.SMTP(host='smtp.gmail.com', port=587)
			# smtpserver.ehlo()
			# smtpserver.starttls()
			# smtpserver.ehlo
			# smtpserver.login("graphspacevt@gmail.com", "vtresearch")
			# header = 'To: ' + email + '\nFrom: ' + 'GraphSpace Admin\n' + 'Subject: Password Reset \n'
			# msg = header + 'Please go to the following url to reset your password: http://localhost:8000/reset?id=' + data[0] + '\n\n' 
			# smtpserver.sendmail("graphspacevt@gmail.com", [email], msg)
			# smtpserver.close()
			mail_title = 'Password Reset!'
			message = 'Please go to the following url to reset your password: http://localhost:8000/reset?id=' + data[0]
			emailFrom = "GraphSpace Admin"
			send_mail(mail_title, message, emailFrom, [email], fail_silently=True)
			return "Email Sent!"
		except lite.Error, e:
			print "Error %s: " %e.args[0]

		finally:
			if con:
				con.close()
	else:
		return None

def retrieveResetInfo(hash):
	con=None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute("select * from user where password = ?", [hash])

		if cur.rowcount == 0:
			return None

		data = cur.fetchone()

		accountToReset = data[0]
		return accountToReset
	except lite.Error, e:
		print "Error %s: " %e.args[0]

	finally:
		if con:
			con.close()

def updateInfo(email, hash):
	con=None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute("update user set password = ? where user_id = ?", (hash, email))

		con.commit();
		return "Password Updated!"
	except lite.Error, e:
		print "Error %s: " %e.args[0]
		return None
	finally:
		if con:
			con.close()

def saveLayout(layout_id, layout_name, owner, graph, user, json, public, unlisted):
	con=None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		print layout_id
		print layout_name
		print owner
		print graph
		print user
		print json
		print public
		print unlisted		

		cur.execute("insert into layout values(?,?,?,?,?,?,?,?)", (None, layout_name, owner, graph, owner, json, 0, 0))
		con.commit()
		return "Layout Updated!"
	except lite.Error, e:
		print "Error %s: " %e.args[0]
		return None
	finally:
		if con:
			con.close()


def getLayout(layout_name, layout_graph, layout_owner):
	con=None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute("select json from layout where layout_name =? and graph_id=? and owner_id=?", (layout_name, layout_graph, layout_owner))
		
		if cur.rowcount == 0:
			return None

		data = cur.fetchone()[0]
		return str(data)

	except lite.Error, e:
		print "Error %s: " %e.args[0]
		return None
	finally:
		if con:
			con.close()

def getLayouts(uid, gid):
	con=None
	try:
		con = lite.connect('test.db')

		cur = con.cursor()
		cur.execute("select layout_name from layout where owner_id =? and graph_id=?", (uid, gid))
		
		if cur.rowcount == 0:
			return None

		data = cur.fetchall()
		cleaned_data = []
		for graphs in data:
			graphs = str(graphs[0])
			cleaned_data.append(graphs)

		return cleaned_data
	except lite.Error, e:
		print "Error %s: " %e.args[0]
		return None
	finally:
		if con:
			con.close()