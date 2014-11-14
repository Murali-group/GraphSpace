# This file is created so that to convert the old schema of the database to the new one
# Run this file on the original database to make it comply with the new standards

import sqlite3 as lite
import sys

con = None

try:
	if len(sys.argv) < 2:
		print "Please enter the name of the database file you want to convert!"
	else:
		con = lite.connect(sys.argv[1])

		cur = con.cursor()
<<<<<<< HEAD

		# cur.execute('insert into edge (head_user_id, head_graph_id, head_id, tail_user_id, tail_graph_id, tail_id, label, directed) select * from tmp_edge')
		# cur.execute('drop table tmp_edge')
		# cur.execute('insert into graph (graph_id, user_id, json, created, modified, public, unlisted) select * from tmp_graph')
		# cur.execute('drop table tmp_graph')	
		# cur.execute('insert into graph_tag (tag_id) select * from tmp_graph_tag')
		# cur.execute('drop table tmp_graph_tag')
		# cur.execute('insert into graph_to_tag (graph_id, user_id, tag_id) select * from tmp_graph_to_tag')
		# cur.execute('drop table tmp_graph_to_tag')
		# cur.execute('insert into group_to_graph (group_id, graph_id, user_id) select * from tmp_group_to_graph')
		# cur.execute('drop table tmp_group_to_graph')
		# cur.execute('insert into group_to_user (user_id, group_id) select * from tmp_group_to_user')
		# cur.execute('drop table tmp_group_to_user')
		# cur.execute('insert into layout (layout_id, layout_name, owner_id, graph_id, user_id, json, public, unlisted) select * from tmp_layout')
		# cur.execute('drop table tmp_layout')
		# cur.execute('insert into node (node_id, label, user_id, graph_id) select * from tmp_node')
		# cur.execute('drop table tmp_node')
		# cur.execute('insert into "group" (group_id, name, owner_id, description, public, unlisted) select * from tmp_group')
		# cur.execute('drop table tmp_group')
		cur.execute('insert into user (user_id, password, activated, activate_code, public, unlisted, admin) select * from tmp_user')
		cur.execute('drop table tmp_user')
=======
		# cur.execute('alter table user RENAME TO user_tmp')
		# cur.execute('create table user (user_id VARCHAR(100) NOT NULL, password VARCHAR(100) NOT NULL, activated INTEGER NOT NULL, activate_code VARCHAR(500), public INTEGER, unlisted INTEGER, refresh INTEGER, admin INTEGER, PRIMARY KEY (user_id))')
		# cur.execute('insert into user (user_id, password, activated, activate_code, public, unlisted, refresh, admin) select id, password, activated, activate_code, public, unlisted, 1, admin from user_tmp')
		# cur.execute('drop table user_tmp')

		cur.execute('alter table graph RENAME TO graph_tmp')
		cur.execute('create table graph (graph_id VARCHAR(500) NOT NULL, user_id VARCHAR(100) NOT NULL, json VARCHAR NOT NULL, created TIMESTAMP NOT NULL, modified TIMESTAMP NOT NULL, public INTEGER, unlisted INTEGER, PRIMARY KEY (graph_id, user_id), FOREIGN KEY(user_id) REFERENCES user (user_id) ON DELETE CASCADE ON UPDATE CASCADE)')
		cur.execute('insert into graph (graph_id, user_id, json, created, modified, public, unlisted) select id, user_id, json, created, modified, public, unlisted from graph_tmp')
		cur.execute('drop table graph_tmp')		

>>>>>>> 6a222f3b86d9c1b92e1b2636da6219167c7cc0d3

		con.commit()

except lite.Error, e:
    
    if con:
        con.rollback()
        
    print "Error %s:" % e.args[0]
    sys.exit(1)
    
finally:
    
    if con:
        con.close() 