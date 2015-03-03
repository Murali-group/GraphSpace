# This file is created so that to convert the old schema of the database to the new one
# Run this file on the original database to make it comply with the new schema

# NOTE: The only difference between the two schemas are some of the column names.  SQLITE doesn't have functionality to change 
# column names, therefore I query all the data, create new tables with the desired column names and insert it accordingly

import sqlite3 as lite
import sys

# Creates temporary tables and adds new tables with updated schema
# Needs a connection to the database and a cursor to communicate with the database
def alter(con, cur):

	# Create placeholders for the old schema tables
	cur.execute('alter table edge rename to tmp_edge')
	cur.execute('alter table graph rename to tmp_graph')
	cur.execute('alter table graph_tag rename to tmp_graph_tag')
	cur.execute('alter table graph_to_tag rename to tmp_graph_to_tag')
	cur.execute('alter table user_group rename to tmp_group')
	cur.execute('alter table group_to_graph rename to tmp_group_to_graph')
	cur.execute('alter table group_to_user rename to tmp_group_to_user')
	cur.execute('alter table layout rename to tmp_layout')
	cur.execute('alter table node rename to tmp_node')
	cur.execute('alter table user rename to tmp_user')

	# Create the new tables with the adjusted schema
	create_tables(con, cur)

	# Go through the old schema tables and collect all the data, inserting it into the new schema table
	cur.execute('insert into edge (head_user_id, head_graph_id, head_id, tail_user_id, tail_graph_id, tail_id, label, directed) select * from tmp_edge')
	cur.execute('insert into graph (graph_id, user_id, json, created, modified, public, unlisted) select * from tmp_graph')
	cur.execute('insert into graph_tag (tag_id) select * from tmp_graph_tag')
	cur.execute('insert into graph_to_tag (graph_id, user_id, tag_id) select * from tmp_graph_to_tag')
	cur.execute('insert into group_to_graph (group_id, user_id, graph_id) select * from tmp_group_to_graph')
	cur.execute('insert into group_to_user (group_id, user_id) select * from tmp_group_to_user')
	cur.execute('insert into layout (layout_id, layout_name, owner_id, graph_id, user_id, json, public, unlisted) select * from tmp_layout')
	cur.execute('insert into node (node_id, label, user_id, graph_id) select * from tmp_node')
	cur.execute('insert into user (user_id, password, activated, activate_code, public, unlisted, admin) select * from tmp_user')
	cur.execute('insert into "group" (group_id, name, owner_id, description, public, unlisted) select * from tmp_group')

	# Commit changes to the database (only needed for insertions)
	con.commit()

# Drops temporary tables from database.
# Run this after you checked that the new tables have been populated correctly.
# Needs a connection to the database and a cursor to communicate with the database
def drop(con, cur):
	cur.execute('drop table tmp_edge')
	cur.execute('drop table tmp_graph')	
	cur.execute('drop table tmp_graph_tag')
	cur.execute('drop table tmp_graph_to_tag')
	cur.execute('drop table tmp_group_to_graph')
	cur.execute('drop table tmp_group_to_user')
	cur.execute('drop table tmp_layout')
	cur.execute('drop table tmp_node')
	cur.execute('drop table tmp_group')
	cur.execute('drop table tmp_user')

# Creates the tables with the modified schema
def create_tables(con, cur):
	cur.execute('CREATE TABLE edge (head_user_id varchar(100) NOT NULL, head_graph_id varchar(500) NOT NULL, head_id varchar(100) NOT NULL, tail_user_id varchar(100) NOT NULL, tail_graph_id varchar(500) NOT NULL, tail_id varchar(100) NOT NULL, label varchar(100), directed integer, PRIMARY KEY (head_user_id, head_graph_id, head_id, tail_user_id, tail_graph_id, tail_id), FOREIGN KEY (head_id, head_user_id, head_graph_id) REFERENCES node(id, user_id, graph_id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (tail_id, tail_user_id, tail_graph_id) REFERENCES node(id, user_id, graph_id) ON DELETE CASCADE ON UPDATE CASCADE)')

	cur.execute('CREATE TABLE graph (graph_id varchar(500) NOT NULL,user_id varchar(100) NOT NULL,json text NOT NULL,created timestamp NOT NULL,modified timestamp NOT NULL,public integer,unlisted integer,PRIMARY KEY (graph_id, user_id),FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE ON UPDATE CASCADE)')

	cur.execute('CREATE TABLE graph_tag (tag_id varchar(100) NOT NULL,PRIMARY KEY (tag_id))')

	cur.execute('CREATE TABLE graph_to_tag (graph_id varchar(500) NOT NULL,user_id varchar(100) NOT NULL,tag_id varchar(100) NOT NULL,PRIMARY KEY (graph_id, user_id, tag_id),FOREIGN KEY (graph_id, user_id) REFERENCES graph(graph_id, user_id) ON DELETE CASCADE ON UPDATE CASCADE,FOREIGN KEY (tag_id) REFERENCES graph_tag(id) ON DELETE CASCADE ON UPDATE CASCADE)')

	# SQLite doesn't like the name group, thus it is surrounded by "group" quotes.
	cur.execute('CREATE TABLE "group" (group_id VARCHAR NOT NULL,name VARCHAR NOT NULL,owner_id VARCHAR NOT NULL,description VARCHAR NOT NULL,public INTEGER,unlisted INTEGER,PRIMARY KEY (group_id),FOREIGN KEY(owner_id) REFERENCES user (user_id) ON DELETE CASCADE ON UPDATE CASCADE)')

	cur.execute('CREATE TABLE group_to_graph (group_id VARCHAR NOT NULL,user_id VARCHAR NOT NULL,graph_id VARCHAR NOT NULL,PRIMARY KEY (group_id, graph_id, user_id),FOREIGN KEY(graph_id, user_id) REFERENCES graph (graph_id, user_id) ON DELETE CASCADE ON UPDATE CASCADE,FOREIGN KEY(group_id) REFERENCES "group" (group_id) ON DELETE CASCADE ON UPDATE CASCADE)')

	cur.execute('CREATE TABLE group_to_user (group_id VARCHAR NOT NULL,user_id VARCHAR NOT NULL,PRIMARY KEY (user_id, group_id),FOREIGN KEY(user_id) REFERENCES user (user_id) ON DELETE CASCADE ON UPDATE CASCADE,FOREIGN KEY(group_id) REFERENCES "group" (group_id) ON DELETE CASCADE ON UPDATE CASCADE)')

	cur.execute('CREATE TABLE layout (layout_id INTEGER NOT NULL,layout_name VARCHAR NOT NULL,owner_id VARCHAR NOT NULL,graph_id VARCHAR NOT NULL,user_id VARCHAR NOT NULL,json VARCHAR NOT NULL,public INTEGER,unlisted INTEGER,PRIMARY KEY (layout_id),FOREIGN KEY(graph_id, user_id) REFERENCES graph (graph_id, user_id) ON DELETE CASCADE ON UPDATE CASCADE,FOREIGN KEY(owner_id) REFERENCES user (user_id) ON DELETE CASCADE ON UPDATE CASCADE)')

	cur.execute('CREATE TABLE node (node_id VARCHAR NOT NULL,label VARCHAR NOT NULL,user_id VARCHAR NOT NULL,graph_id VARCHAR NOT NULL,PRIMARY KEY (node_id, user_id, graph_id),FOREIGN KEY(user_id, graph_id) REFERENCES graph (user_id, graph_id) ON DELETE CASCADE ON UPDATE CASCADE)')

	cur.execute('CREATE TABLE user (user_id VARCHAR NOT NULL,password VARCHAR NOT NULL,activated INTEGER NOT NULL,activate_code VARCHAR,public INTEGER,unlisted INTEGER,admin INTEGER,PRIMARY KEY (user_id))')

# Main method that checks arguments and alters the database
# In order to run, navigate to terminal in the directory of this file and type: python alter_table.py alter [NAME_OF_DB_FILE]
# Be patient. When the script is done, you will regain control of the terminal. Until then, please do not exit out of the process.
# After the process has finished, please verify that the database has the correct columns.  Next, run: python alter_table.py drop [NAME_OF_DB_FILE]
# to drop all of the temporary tables that were used.
def main():
	if (len(sys.argv) < 2):
		print "Please enter the name of the database file you want to convert!"
	elif len(sys.argv) < 3:
		print "Please enter the command of the script you want to run! Ex: alter or drop"
	else:
		con = None
		try:
			# Connects to file name in database
			con = lite.connect(sys.argv[1])
			cur = con.cursor()

			if sys.argv[2] == 'alter':
				alter(con, cur)
			# Call this after you're sure that you're data has been successfully moved! 
			# This is so data doesn't get deleted without double-checking!
			elif sys.argv[2] == 'drop':
				drop(con, cur)
				# After running this, be sure to run: python manage.py syncdb
			else:
				print "Unrecognized input!"

		except lite.Error, e:
	    
		    if con:
		        con.rollback()
	        
		    print "Error %s:" % e.args[0]
		    sys.exit(1)
	    
		finally:
		    
		    if con:
		        con.close() 

# Python way of running 'main' method
if __name__ == '__main__':
	main()