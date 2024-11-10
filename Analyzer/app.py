from connexion import App
from flask import Flask, jsonify
import yaml
import logging.config
from pykafka import KafkaClient
import json
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
# Initialize Connexion app
app = App(__name__, specification_dir="./")
app.add_api("openapi.yml")

# Load app config and logger
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

# Constants for Kafka topic and server
hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
client = KafkaClient(hosts=hostname)
topic = client.topics[str.encode(app_config["events"]["topic"])]

# Function to get a specific movie event by index
def get_movie_event(index):
    """ Get Movie at a specified index """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    
    logger.info("Retrieving movie at index %d" % index)
    count = 0
    
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
        
            if msg['type'] == 'add_movie':
                if count == index:
                    return msg['payload'], 200
                count += 1
            
    except Exception as e:
        logger.error("No more messages found")
        logger.error("Could not find movie at index %d: %s" % (index, str(e)))
    
    return {"message": "Not Found"}, 404

# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8110)
