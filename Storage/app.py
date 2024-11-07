import connexion
from connexion import NoContent
from datetime import datetime
from requests import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from movie import Movie  
from review import Review 
from base import Base  
import os
import yaml
import logging
import logging.config
from sqlalchemy import and_
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

# Load configuration files
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

# Set up the MySQL connection using the data from app_conf.yml
DB_ENGINE = create_engine(
    f'mysql+pymysql://{app_config["datastore"]["user"]}:{app_config["datastore"]["password"]}@{app_config["datastore"]["hostname"]}:{app_config["datastore"]["port"]}/{app_config["datastore"]["db"]}'
)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE) 

Base.metadata.create_all(DB_ENGINE)

logger.info(f'Connecting to DB. Hostname: {app_config["datastore"]["hostname"]}, Port: {app_config["datastore"]["port"]}')

# Function to get movies created between specified timestamps
def get_movies_by_timestamp(start_timestamp, end_timestamp):
    session = DB_SESSION() 
    
    start_timestamp_datetime = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_timestamp_datetime = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    results = session.query(Movie).filter(
        and_(Movie.date_created >= start_timestamp_datetime,
             Movie.date_created < end_timestamp_datetime)
    ).all()
    
    results_list = [movie.to_dict() for movie in results]

    session.close()
    logger.info("Query for movies between %s and %s returns %d results" %
                (start_timestamp, end_timestamp, len(results_list)))
    
    return results_list, 200

def get_reviews_by_timestamp(start_timestamp, end_timestamp):
    session = DB_SESSION()
    
    start_timestamp_datetime = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_timestamp_datetime = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    results = session.query(Review).filter(
        and_(Review.date_created >= start_timestamp_datetime,
             Review.date_created < end_timestamp_datetime)
    ).all()
    
    results_list = [review.to_dict() for review in results]

    session.close()
    logger.info("Query for reviews between %s and %s returns %d results" %
                (start_timestamp, end_timestamp, len(results_list)))
    
    return results_list, 200

def process_messages():
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"]) # kafka configuration
    client = KafkaClient(hosts=hostname) # Create a Kafka instance
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    # A consumer that only reads new messages
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                          reset_offset_on_start=False,
                                          auto_offset_reset=OffsetType.LATEST)
    
    for msg in consumer:
        msg_str = msg.value.decode('utf-8') # Msg are converted from bytes to string
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]

        # Create a session for each message
        db_session = sessionmaker(bind=DB_ENGINE)()

        try:
            # Check message type and insert into the correct table
            if msg["type"] == "add_movie":
                movie = Movie(
                    movie_id=payload["movie_id"],  
                    title=payload["title"],         
                    release_date=payload["release_date"],  
                    length=payload.get("length"),   
                    genre=payload["genre"],         
                    cast=payload["cast"],          
                    director=payload["director"],   
                    trace_id=payload["trace_id"]   
            )
                db_session.add(movie)
                logger.info("Stored movie event to database: %s" % payload)

            elif msg["type"] == "submit_review":
                review = Review(
                    user_id=payload["user_id"],
                    movie_id=payload["movie_id"],
                    rating=payload.get("rating"),
                    comment=payload.get("comment", ""),
                    trace_id=payload["trace_id"]
                )
                db_session.add(review)
                logger.info("Stored review event to database: %s" % payload)

            # Commit the transaction for the current message
            db_session.commit()

            # Commit message will not be consumed again
            consumer.commit_offsets()    
        except Exception as e:
            db_session.rollback()  # Rollback if there’s an error
            logger.error(f"Failed to process message: {msg}. Error: {e}")
            
        finally:
            db_session.close()

app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(host="0.0.0.0", port=8090)