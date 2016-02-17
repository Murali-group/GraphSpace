import sqlite3
import datetime

'''
	Removes all public graphs uploaded anonymously (without a user logging into GraphSpace) 
	that are older than 30 days.

	@param cur: Database cursor
'''
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
		created = datetime.datetime.strptime(task[4], '%Y-%m-%d %H:%M:%S.%f')

		if created < datetime.datetime.now() + datetime.timedelta(days=-3):
			print "Deleting expired task owned by", task_owner, "for graph:", graph_id, "owned by", user_id 
			cur.execute('delete from task where task_id = ?', (task_id, ))

if __name__ == "__main__":
    conn = sqlite3.connect('graphspace.db')
    cur = conn.cursor()

    print "Running Cron Job to remove expired data from database"
    
    removeExpiredPublicGraphs(cur)
    removeExpiredTasks(cur)

    conn.commit()
    conn.close()
