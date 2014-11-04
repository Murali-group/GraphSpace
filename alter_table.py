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
		# cur.execute('alter table user RENAME TO user_tmp')
		# cur.execute('create table user (user_id VARCHAR(100) NOT NULL, password VARCHAR(100) NOT NULL, activated INTEGER NOT NULL, activate_code VARCHAR(500), public INTEGER, unlisted INTEGER, refresh INTEGER, admin INTEGER, PRIMARY KEY (user_id))')
		# cur.execute('insert into user (user_id, password, activated, activate_code, public, unlisted, refresh, admin) select id, password, activated, activate_code, public, unlisted, 1, admin from user_tmp')
		# cur.execute('drop table user_tmp')

		cur.execute('alter table graph RENAME TO graph_tmp')
		cur.execute('create table graph (graph_id VARCHAR(500) NOT NULL, user_id VARCHAR(100) NOT NULL, json VARCHAR NOT NULL, created TIMESTAMP NOT NULL, modified TIMESTAMP NOT NULL, public INTEGER, unlisted INTEGER, PRIMARY KEY (graph_id, user_id), FOREIGN KEY(user_id) REFERENCES user (user_id) ON DELETE CASCADE ON UPDATE CASCADE)')
		cur.execute('insert into graph (graph_id, user_id, json, created, modified, public, unlisted) select id, user_id, json, created, modified, public, unlisted from graph_tmp')
		cur.execute('drop table graph_tmp')		


		con.commit()

except lite.Error, e:
    
    if con:
        con.rollback()
        
    print "Error %s:" % e.args[0]
    sys.exit(1)
    
finally:
    
    if con:
        con.close() 