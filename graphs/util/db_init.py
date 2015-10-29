'''
    Module to initialize database access.
'''

from graphs.util.db_conn import Database

#connect to database
db = Database('prod')

#get tables from database
graph = db.meta.tables['graph']
node = db.meta.tables['node']
edge = db.meta.tables['edge']
user = db.meta.tables['user']
group = db.meta.tables['group']
group_to_graph = db.meta.tables['group_to_graph']
graph_to_tag = db.meta.tables['graph_to_tag']
password_reset = db.meta.tables['password_reset']