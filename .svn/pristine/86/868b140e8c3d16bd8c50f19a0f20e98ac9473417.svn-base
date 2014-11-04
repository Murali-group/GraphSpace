import models as m
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from parse_json import parse

originaldb = 'sqlite:////data/craigy/graphspace-development/graphspace-server/graphspace_old.db'

testdb = 'sqlite:///test_ddl.db'


engine = create_engine(testdb, echo=False)

#m.Base.metadata.bind = engine
#m.Base.metadata.create_all(engine)

#create session to query from the database
Session = sessionmaker(bind=engine)
session = Session()

#User objects to insert
#session.add_all([
#        m.User(user_id='user1', password='pw', activated=1, activate_code='code', public=1, unlisted=0, admin=0),
#        m.User(user_id='admin', password='pw', activated=1, activate_code='code', public=1, unlisted=0, admin=1),
#        m.User(user_id='user2', password='pw', activated=1, activate_code='code', public=1, unlisted=0, admin=0),
#        m.User(user_id='user3', password='pw', activated=1, activate_code='code', public=1, unlisted=0, admin=0),
#        m.User(user_id='user4', password='pw', activated=1, activate_code='code', public=1, unlisted=0, admin=0)
#        ])

#insert into database
#session.commit()

result = session.query('json').filter(m.Graph.user_id=='ategge@vt.edu').first()[0]

parse(result)
