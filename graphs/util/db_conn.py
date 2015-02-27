from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import sqlalchemy
import graphs.models as models

# database locations
_originaldb = 'sqlite:////Users/Divit/Documents/GRA/GraphSpace/graphspace.db'

_devdb = 'sqlite:////usr/local/yijaeil/graphspace-server/graphspace_live_backup.db'

_devdb2 = 'sqlite:////data/craigy/graphspace-development/graphspace-server/graphspace_old.db'

_testdb = 'sqlite:///test.db'

class Database(object):
    '''
        Create a database object to query from.
    '''
    def __init__(self, db_type):
        self.db = db_type
        self.connection = None

        if self.db == 'prod':
            self.engine = create_engine(_originaldb, echo=False)
        elif self.db == 'dev':
            self.engine = create_engine(_devdb, echo=False, poolclass=NullPool)
        elif self.db == 'dev2':
            self.engine = create_engine(_devdb2, echo=False, poolclass=NullPool)
        elif self.db == 'test':
            self.engine = create_engine(_testdb, echo=False)
            models.Base.metadata.bind = self.engine
            models.Base.metadata.create_all(self.engine)
        else:
            self.engine = create_engine('sqlite:///:memory:', echo=False)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        if self.db == 'prod' or self.db == 'dev' or self.db == 'dev2':
            self.meta = sqlalchemy.schema.MetaData()
            self.meta.reflect(bind=self.engine)
        elif self.db == 'test':
            self.meta = models.Base.metadata
        else:
            self.meta = None

    def new_session(self):
        '''
            Create a new session in this database. This is needed to avoid 1 seesion per thread
            error raised if you don't create a new session for every new page load or query request.
        '''
        self.session.close()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        return self.session
    
    def connect(self):
        '''
            Establish connection to the database engine.
        '''
        self.connection = self.engine.connect()
        return self.connection

    def close(self):
        '''
            Close the connection to the database engine.
        '''
        if self.connection is not None:
            self.connection.close()
