from sqlalchemy.orm import Session
from database.connection import engine
import logging

def get_db(): 
    with Session(engine) as session:
        yield session 
    
def get_transactional_db():
    with Session(engine) as session:
        try:
            yield session
            session.commit()
            
            logger = logging.getLogger("wms")
            events = session.info.pop("log_events", [])

            for event in events:          
                logger.info(event)

        except Exception:
            session.rollback()
            session.info.pop("log_events", None)
            raise
            
