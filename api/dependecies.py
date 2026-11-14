from sqlalchemy.orm import Session
from database.connection import engine

def get_db(): 
    with Session(engine) as session:
        yield session 
    
def get_transactional_db():
    with Session(engine) as session:
        try:
            yield session
            session.commit()

        except Exception:
            session.rollback()
            raise
            
