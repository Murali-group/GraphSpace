'''
    Module to initialize database access.
'''

from graphs.util.db_conn import Database

#connect to database
db = Database('test')

#get tables from database
graph = db.meta.tables['graph']
user = db.meta.tables['user']
group = db.meta.tables['group']
group_to_graph = db.meta.tables['group_to_graph']
