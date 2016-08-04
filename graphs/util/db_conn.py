from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from django.conf import settings

# database locations
# _originaldb = settings.DATABASE_LOCATION
config = settings.DATABASES['default']

class Database(object):
    '''
        Create a database object to query from.
    '''
    def __init__(self, db_type):
        self.db = db_type
        self.connection = None

        if self.db == 'prod':
            self.engine = create_engine(''.join(['postgresql://', config['USER'], ':', config['PASSWORD'], '@', config['HOST'], ':', config['PORT'], '/', config['NAME']]), echo=False)

        else:
            self.engine = create_engine('sqlite:///:memory:', echo=False)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        if self.db == 'prod':
            self.meta = sqlalchemy.schema.MetaData()
            self.meta.reflect(bind=self.engine)
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

    from contextlib import contextmanager

    @contextmanager
    def session_scope():
        """Provide a transactional scope around a series of operations."""
        session = Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()