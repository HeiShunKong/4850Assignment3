import json
import logging
from pykafka import KafkaClient
from flask import Flask, jsonify, request
from connexion import App
import yaml
import logging.config

# Initialize Flask and Connexion app
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
    
    # Reset offset on start to retrieve messages from the beginning of the queue.
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    
    logger.info("Retrieving movie at index %d" % index)
    count = 0  # To track the index of the retrieved message
    
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
        
            if msg['type'] == 'add_movie':
                # Increment count only if the event type is correct
                if count == index:
                    return msg['payload'],200 # Return the movie event and code 200
                count += 1
            
    except Exception as e:
        logger.error("No more messages found")
        logger.error("Could not find movie at index %d: %s" % (index, str(e)))
    
    return {"message": "Not Found"}, 404  # Return Not Found if index does not exist


# Function to get a specific review event by index
def get_review_event(index):
    """ Get Review at a specified index """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    # Reset offset on start to retrieve messages from the beginning of the queue.
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    
    logger.info("Retrieving review at index %d" % index)
    count = 0  # To track the index of the retrieved message
    
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            
            # Check for the event type and index
            if msg['type'] == 'submit_review':
                # Increment count only if the event type is correct
                if count == index:
                    return msg['payload'],200 # Return the movie event and code 200
                count += 1
            
    except Exception as e:
        logger.error("No more messages found")
        logger.error("Could not find review at index %d: %s" % (index, str(e)))
    
    return {"message": "Not Found"}, 404  # Return Not Found if index does not exist

# Function to get statistics of all events in the queue
def get_event_stats():
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    stats = {"num_movies": 0, "num_reviews": 0}
    logger.info("Calculating event statistics")

    try:
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

# Add routes to Flask app
app.app.add_url_rule("/event1", "get_movie_event", get_movie_event)
app.app.add_url_rule("/event2", "get_review_event", get_review_event)
app.app.add_url_rule("/stats", "get_event_stats", get_event_stats)

if __name__ == "__main__":
    app.run(port=8110)