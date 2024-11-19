import connexion
from connexion import NoContent
import logging
import logging.config
import uuid
import datetime
import json
from pykafka import KafkaClient
import time
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    
logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

# Kafka Configuration
kafka_hostname = app_config['events']['hostname']
kafka_port = app_config['events']['port']
topic_name = app_config['events']['topic']

# Initialization and Retry 
kafka_client = None
topic = None

def initialize_kafka_client(retries=5, retry_interval=5):
    global kafka_client, topic
    retry_count = 0
    while retry_count < retries:
        try:
            kafka_client = KafkaClient(hosts=f'{kafka_hostname}:{kafka_port}')
            topic = kafka_client.topics[str.encode(topic_name)]
            logger.info(f"Connected to Kafka at {kafka_hostname}:{kafka_port}, topic {topic_name} initialized.")
            return True
        except Exception as e:
            retry_count += 1
            logger.error(f"Error connecting to Kafka: {str(e)}. Retry {retry_count}/{retries}.")
            time.sleep(retry_interval)
    
    logger.error("Failed to connect to Kafka after multiple attempts.")
    return False

# Check if Kafka is available
def check_kafka_health():
    try:
        kafka_client.topics[str.encode(topic_name)]  # Check if the topic is accessible
        logger.info("Kafka is healthy and the topic is accessible.")
        return True
    except Exception as e:
        logger.error(f"Kafka health check failed: {str(e)}")
        return False

# Initialize Kafka connection on startup
if not initialize_kafka_client():
    logger.error("Kafka connection failed during startup. Exiting.")
    exit(1)

# Endpoint functions

def add_movie(body):
    trace_id = str(uuid.uuid4())  # Generate a unique trace_id for the event
    logger.info(f"Received event add movie request with a trace id of {trace_id}") 
    body['trace_id'] = trace_id  # Include trace_id in the request body to pass it to the next service

    # Produce message to Kafka
    producer = topic.get_sync_producer()  # Use the already initialized producer

    msg = {
        "type": "add_movie",  # Event type for adding a movie
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),  # Current datetime 
        "payload": body  # The event object is the body of the request
    }

    msg_str = json.dumps(msg)  # Convert the message dictionary to a JSON string
    producer.produce(msg_str.encode('utf-8'))  # Produce the message to Kafka

    logger.info(f"Produced event message for add movie (Id: {trace_id})")

    return NoContent, 201 

def submit_review(body):
    trace_id = str(uuid.uuid4())  
    logger.info(f"Received event submit review request with a trace id of {trace_id}")  
    body['trace_id'] = trace_id  

    # Produce message to Kafka
    producer = topic.get_sync_producer()  # Use the already initialized producer
    
    msg = {
        "type": "submit_review",  
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),  
        "payload": body  
    }

    msg_str = json.dumps(msg)  
    producer.produce(msg_str.encode('utf-8'))  

    logger.info(f"Produced event message for submit review (Id: {trace_id})")

    return NoContent, 201  # Hard-coded status code for success
app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
