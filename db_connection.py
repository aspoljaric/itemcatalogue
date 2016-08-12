from database import Base, Category, Item, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager


def connect():
    """Connect to the SQLite database.  Returns a database session."""
    try:
        engine = create_engine('sqlite:///categories.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        return session
    except:
        print("Connection failed.")


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = connect()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
