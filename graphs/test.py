from django.shortcuts import render_to_response
import sqlalchemy, sqlalchemy.orm
import models

engine = sqlalchemy.create_engine('sqlite:///test_ddl.db', echo=False)
models.Base.metadata.bind = engine
Session = sqlalchemy.orm.sessionmaker(bind=engine)
s = Session()

def index(request):
    result = s.query(models.User).filter(models.User.admin==0)
    return render_to_response('graph/index.html', {'result':result})

for u in s.query(models.User).filter(models.User.admin==0):
    print u.user_id
