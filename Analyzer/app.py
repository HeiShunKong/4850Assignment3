from connexion import App
from flask import jsonify
import yaml
import logging.config
from pykafka import KafkaClient
import json
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
import os

# Initialize Connexion app
app = App(__name__, specification_dir="./")
app.add_api("openapi.yml")

# Load app config and logger based on environment (test/dev)
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

# Load the app configuration
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# Load logging configuration
with open(log_conf_file, 'r') as f:
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
    logger.info("Retrieving movie at index %d" % index)
    count = 0

    try:
        # Consume Kafka messages for the movie topic
        consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg['type'] == 'add_movie':
                if count == index:
                    return msg['payload'], 200
                count += 1
    except Exception as e:
        logger.error("No more messages found or error while processing: %s" % str(e))

    return {"message": "Not Found"}, 404

# Function to get a specific review event by index
def get_review_event(index):
    """ Get Review at a specified index """
    logger.info("Retrieving review at index %d" % index)
    count = 0  # To track the index of the retrieved message

    try:
        # Consume Kafka messages for the review topic
        consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            # Check for the event type and index
            if msg['type'] == 'submit_review':
                if count == index:
                    return msg['payload'], 200
                count += 1
    except Exception as e:
        logger.error("No more messages found or error while processing: %s" % str(e))

    return {"message": "Not Found"}, 404

def get_event_stats():
    """ Calculate event statistics like number of movies and reviews """
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    stats = {"num_movies": 0, "num_reviews": 0}
    logger.info("Calculating event statistics")

    try:
        # Consume Kafka messages to calculate statistics
        for msg in consumer:
            msg_str = msg.value.decode("utf-8")
            event = json.loads(msg_str)
            if event["type"] == "add_movie":
                stats["num_movies"] += 1
            elif event["type"] == "submit_review":
                stats["num_reviews"] += 1
    except Exception as e:
        logger.error("Error calculating stats: %s", str(e))

    return jsonify(stats), 200

# Add CORS middleware to the app for cross-origin requests
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
